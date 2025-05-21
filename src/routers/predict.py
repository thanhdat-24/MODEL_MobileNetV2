from collections import defaultdict
import os
from flask import Blueprint, current_app, request, jsonify, session
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
import json
from services.supabase_service import get_supabase_client
from services.image_service import preprocess_image
from services.openai_service import check_image_content
from config import TRAIN_DIR

predict_bp = Blueprint('predict', __name__)

# Global variables for model and configuration
_model = None
_class_names = None

def get_system_config():
    """Lấy cấu hình hệ thống từ file config hoặc database"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error loading system config: {str(e)}")
            else:
                print(f"Error loading system config: {str(e)}")
    
    # Return default config if file doesn't exist or can't be loaded
    from config import MODEL_SAVE_PATH, IMG_SIZE, CONFIDENCE_THRESHOLD
    return {
        'model_path': MODEL_SAVE_PATH,
        'img_size': IMG_SIZE,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'max_predictions': 5,
        'enable_image_check': True
    }

def get_model():
    """Lấy mô hình đã được load, nếu chưa load thì load từ cấu hình hiện tại"""
    global _model
    if _model is None:
        load_model()
    return _model

def get_class_names():
    """Lấy danh sách tên lớp"""
    global _class_names
    if _class_names is None:
        _class_names = sorted([d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))])
    return _class_names

def load_model():
    """Load mô hình từ file cấu hình"""
    global _model
    try:
        # Lấy đường dẫn mô hình từ cấu hình
        config = get_system_config()
        model_path = config['model_path']
        
        log_message = f"Loading model from {model_path}"
        if hasattr(current_app, 'logger'):
            current_app.logger.info(log_message)
        else:
            print(log_message)
            
        _model = tf.keras.models.load_model(model_path)
        
        log_message = "Model loaded successfully"
        if hasattr(current_app, 'logger'):
            current_app.logger.info(log_message)
        else:
            print(log_message)
            
        return True
    except Exception as e:
        error_message = f"Error loading model: {str(e)}"
        if hasattr(current_app, 'logger'):
            current_app.logger.error(error_message)
        else:
            print(error_message)
            
        # Fallback to default model if loading fails
        from config import MODEL_SAVE_PATH
        try:
            _model = tf.keras.models.load_model(MODEL_SAVE_PATH)
            log_message = f"Fallback model loaded from {MODEL_SAVE_PATH}"
            if hasattr(current_app, 'logger'):
                current_app.logger.info(log_message)
            else:
                print(log_message)
                
            return True
        except Exception as fallback_error:
            error_message = f"Error loading fallback model: {str(fallback_error)}"
            if hasattr(current_app, 'logger'):
                current_app.logger.error(error_message)
            else:
                print(error_message)
                
            return False

def reload_model():
    """Tải lại mô hình (gọi khi thay đổi cấu hình)"""
    global _model
    # Xóa mô hình hiện tại để load mô hình mới
    _model = None
    # Load mô hình mới
    return load_model()

# Setup function to initialize model when the blueprint is registered
def init_app(app):
    """Initialize the blueprint with the app"""
    with app.app_context():
        load_model()

@predict_bp.route("/predict", methods=["POST"])
def predict():
    # Lấy mô hình và cấu hình
    model = get_model()
    config = get_system_config()
    class_names = get_class_names()
    
    if not model:
        return jsonify({"error": "Model not available"}), 500
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
        
        # Chuyển ảnh thành base64
        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_base64 = "data:image/png;base64," + base64.b64encode(img_io.getvalue()).decode()

        # Kiểm tra ảnh có chứa hoa quả hay không bằng OpenAI
        skip_check = request.form.get("skip_check", "false").lower() == "true"
        
        current_app.logger.info(f"Kiểm tra ảnh: skip_check={skip_check}, enable_check={config.get('enable_image_check', True)}")

        if config.get('enable_image_check', True) and not skip_check:
            current_app.logger.info("Đang gọi API OpenAI để kiểm tra ảnh...")
            is_valid, _ = check_image_content(img_base64)
            current_app.logger.info(f"Kết quả kiểm tra ảnh: {is_valid}")
            if not is_valid:
                # Lưu lịch sử nhận diện thất bại nếu cần
                if "user_id" in session:
                    try:
                        supabase = get_supabase_client()
                        history_data = {
                            "user_id": session["user_id"],
                            "hinh_anh": img_base64,
                            "ket_qua": json.dumps([{"label": "Không phải hoa quả", "confidence": 0.0}]),
                            "ten_san_pham": "Không hợp lệ",
                            "do_chinh_xac": 0.0,
                            "nhan_dien_thanh_cong": False,
                            "loai_nhan_dien": "don_anh"
                        }
                        
                        supabase.table('lichsunhandien').insert(history_data).execute()
                    except Exception as e:
                        current_app.logger.error(f"Lỗi khi lưu lịch sử: {e}")
                
                # Trả về thông báo lỗi thân thiện hơn
                return jsonify({
                    "success": False,
                    "image": img_base64,
                    "error": "Ảnh không hợp lệ",
                    "message": "Ảnh không phải là trái cây, rau, củ, quả hoặc chất lượng ảnh không phù hợp. Vui lòng chọn ảnh khác hoặc xem hướng dẫn sử dụng để có kết quả tốt nhất."
                }), 400

        processed_image = preprocess_image(image)

        # Dự đoán
        predictions = model.predict(processed_image)[0]
        
        # Lấy số lượng kết quả và ngưỡng độ tin cậy từ cấu hình
        max_predictions = config.get('max_predictions', 5)
        confidence_threshold = config.get('confidence_threshold', 0.5)
        
        # Chỉ hiển thị kết quả trên ngưỡng tin cậy
        predictions_filtered = [(i, predictions[i]) for i in range(len(predictions)) if predictions[i] >= confidence_threshold]
        # Sắp xếp và chỉ lấy top N
        predictions_top = sorted(predictions_filtered, key=lambda x: x[1], reverse=True)[:max_predictions]
        
        prediction_results = []
        for idx, prob in predictions_top:
            prediction_results.append({"label": class_names[idx], "confidence": float(prob)})
        
        # Bổ sung dummy result nếu không có kết quả nào vượt ngưỡng
        if not prediction_results:
            top_idx = predictions.argmax()
            prediction_results.append({
                "label": class_names[top_idx],
                "confidence": float(predictions[top_idx]),
                "below_threshold": True
            })

        # Lưu lịch sử
        if "user_id" in session and prediction_results:
            try:
                supabase = get_supabase_client()
                history_data = {
                    "user_id": session["user_id"],
                    "hinh_anh": img_base64,
                    "ket_qua": json.dumps(prediction_results),
                    "ten_san_pham": prediction_results[0]["label"],
                    "do_chinh_xac": float(prediction_results[0]["confidence"]),
                    "nhan_dien_thanh_cong": True,
                    "loai_nhan_dien": "don_anh"
                }
                supabase.table('lichsunhandien').insert(history_data).execute()
            except Exception as e:
                current_app.logger.error(f"Lỗi khi lưu lịch sử: {e}")

        return jsonify({
            "success": True,
            "image": img_base64,
            "predictions": prediction_results
        })
    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Error processing image", "details": str(e)}), 500

@predict_bp.route("/predict-multi", methods=["POST"])
def predict_multi():
    # Lấy mô hình và cấu hình
    model = get_model()
    config = get_system_config()
    class_names = get_class_names()
    
    if not model:
        return jsonify({"error": "Model not available"}), 500
    
    if "files[]" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist("files[]")
    if not files or len(files) == 0:
        return jsonify({"error": "No files selected"}), 400

    try:
        results = []
        thumbnails = []
        group_results = defaultdict(lambda: {"count": 0, "confidence": 0.0})
        individual_history_ids = []
        invalid_images = []
        
        # Lấy ngưỡng độ tin cậy từ cấu hình
        confidence_threshold = config.get('confidence_threshold', 0.5)
        
        # Kiểm tra xem có cần bỏ qua kiểm tra hay không
        skip_check = request.form.get("skip_check", "false").lower() == "true"
        
        for idx, file in enumerate(files):
            if file.filename == '':
                continue
                
            image = Image.open(io.BytesIO(file.read()))
            
            img_io = io.BytesIO()
            image.save(img_io, format="PNG")
            img_base64 = "data:image/png;base64," + base64.b64encode(img_io.getvalue()).decode()
            
            # Kiểm tra ảnh có chứa hoa quả hay không bằng OpenAI
            if config.get('enable_image_check', True) and not skip_check:
                is_valid, _ = check_image_content(img_base64)
                if not is_valid:
                    invalid_images.append({
                        "image": img_base64,
                        "message": "Ảnh không phải là trái cây, rau, củ, quả hoặc chất lượng ảnh không phù hợp. Vui lòng chọn ảnh khác hoặc xem hướng dẫn sử dụng để có kết quả tốt nhất."
                    })
                    continue
            
            processed_image = preprocess_image(image)
            
            predictions = model.predict(processed_image)[0]
            
            # Lọc các kết quả dựa trên ngưỡng tin cậy
            valid_predictions = [(i, predictions[i]) for i in range(len(predictions)) if predictions[i] >= confidence_threshold]
            
            # Nếu không có kết quả nào vượt ngưỡng, lấy kết quả cao nhất
            if not valid_predictions:
                top_idx = predictions.argmax()
                top_label = class_names[top_idx]
                top_prob = float(predictions[top_idx])
            else:
                # Lấy kết quả đầu tiên (cao nhất) từ danh sách đã lọc
                top_idx, top_prob = valid_predictions[0]
                top_label = class_names[top_idx]
            
            result = {
                "image": img_base64,
                "label": top_label,
                "confidence": float(top_prob)
            }
            
            if "user_id" in session:
                try:
                    supabase = get_supabase_client()
                    individual_history = {
                        "user_id": session["user_id"],
                        "hinh_anh": img_base64,
                        "ket_qua": json.dumps([{"label": top_label, "confidence": float(top_prob)}]),
                        "ten_san_pham": top_label,
                        "do_chinh_xac": float(top_prob),
                        "nhan_dien_thanh_cong": True,
                        "loai_nhan_dien": "da_anh"
                    }
                    
                    response = supabase.table('lichsunhandien').insert(individual_history).execute()
                    if response.data and len(response.data) > 0:
                        individual_history_ids.append(response.data[0]['id'])
                    
                except Exception as e:
                    current_app.logger.error(f"Lỗi khi lưu lịch sử ảnh {idx+1}: {e}")
            
            results.append(result)
            thumbnails.append({
                "image": img_base64,
                "label": top_label,
                "confidence": float(top_prob)
            })
            
            if top_prob > group_results[top_label]["confidence"]:
                group_results[top_label]["confidence"] = float(top_prob)
            group_results[top_label]["count"] += 1
            group_results[top_label]["label"] = top_label

        if not results:
            return jsonify({
                "success": False,
                "error": "Không tìm thấy hình ảnh hoa quả hợp lệ nào",
                "invalid_images": invalid_images
            }), 400

        grouped_results = sorted(
            [value for value in group_results.values()],
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        # Đảm bảo tất cả giá trị float đã được chuyển đổi
        for group in grouped_results:
            if "confidence" in group:
                group["confidence"] = float(group["confidence"])

        if "user_id" in session and grouped_results and len(thumbnails) > 0:
            try:
                supabase = get_supabase_client()
                nhom_ids = []
                
                for group in grouped_results:
                    representative_image = next((t["image"] for t in thumbnails if t["label"] == group["label"]), thumbnails[0]["image"])
                    
                    group_data = {
                        "user_id": session["user_id"],
                        "hinh_anh_dai_dien": representative_image,
                        "ten_nhom": group["label"],
                        "so_luong": group["count"],
                        "do_chinh_xac": float(group["confidence"]),
                        "nhan_dien_thanh_cong": True
                    }
                    
                    response = supabase.table('nhom_ket_qua').insert(group_data).execute()
                    
                    if response.data and len(response.data) > 0:
                        nhom_id = response.data[0]['id']
                        nhom_ids.append(nhom_id)
                        
                        for history_id in individual_history_ids:
                            individual_result = next((r for r in results if r["label"] == group["label"]), None)
                            if individual_result:
                                link_data = {
                                    "nhom_id": nhom_id,
                                    "lichsu_id": history_id
                                }
                                supabase.table('ket_qua_nhom').insert(link_data).execute()
                
            except Exception as e:
                current_app.logger.error(f"Lỗi khi lưu thông tin nhóm: {e}")

        return jsonify({
            "success": True,
            "group_results": grouped_results,
            "thumbnails": thumbnails,
            "total_images": len(results),
            "total_uploaded": len(files),
            "invalid_images": invalid_images
        })
    except Exception as e:
        current_app.logger.error(f"Error processing multiple images: {e}")
        return jsonify({"error": f"Error processing images: {str(e)}"}), 500

# Do not load the model at module level - will be loaded when needed or on init_app
