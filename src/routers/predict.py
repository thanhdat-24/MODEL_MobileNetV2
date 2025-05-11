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
from config import MODEL_SAVE_PATH, TRAIN_DIR

predict_bp = Blueprint('predict', __name__)

# Load mô hình đã train
model = tf.keras.models.load_model(MODEL_SAVE_PATH)

# Lấy danh sách lớp từ thư mục dataset
class_names = sorted([d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))])

@predict_bp.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)

        # Chuyển ảnh thành base64
        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_base64 = "data:image/png;base64," + base64.b64encode(img_io.getvalue()).decode()

        # Dự đoán
        predictions = model.predict(processed_image)[0]
        top_5_indices = predictions.argsort()[-5:][::-1]
        top_5_labels = [class_names[idx] for idx in top_5_indices]
        top_5_probs = [float(predictions[idx]) for idx in top_5_indices]

        prediction_results = []
        for label, conf in zip(top_5_labels, top_5_probs):
            prediction_results.append({"label": label, "confidence": conf})

        # Lưu lịch sử
        if "user_id" in session:
            try:
                supabase = get_supabase_client()
                history_data = {
                    "user_id": session["user_id"],
                    "hinh_anh": img_base64,
                    "ket_qua": json.dumps(prediction_results),
                    "ten_san_pham": top_5_labels[0],
                    "do_chinh_xac": float(top_5_probs[0]),
                    "nhan_dien_thanh_cong": True,
                    "loai_nhan_dien": "don_anh"
                }
                supabase.table('lichsunhandien').insert(history_data).execute()
            except Exception as e:
                current_app.logger.error(f"Lỗi khi lưu lịch sử: {e}")

        return jsonify({
            "image": img_base64,
            "predictions": prediction_results
        })
    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Error processing image"}), 500

@predict_bp.route("/predict-multi", methods=["POST"])
def predict_multi():
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
        
        for idx, file in enumerate(files):
            if file.filename == '':
                continue
                
            image = Image.open(io.BytesIO(file.read()))
            processed_image = preprocess_image(image)
            
            img_io = io.BytesIO()
            image.save(img_io, format="PNG")
            img_base64 = "data:image/png;base64," + base64.b64encode(img_io.getvalue()).decode()
            
            predictions = model.predict(processed_image)[0]
            top_idx = predictions.argmax()
            top_label = class_names[top_idx]
            top_prob = float(predictions[top_idx])
            
            result = {
                "image": img_base64,
                "label": top_label,
                "confidence": top_prob
            }
            
            if "user_id" in session:
                try:
                    supabase = get_supabase_client()
                    individual_history = {
                        "user_id": session["user_id"],
                        "hinh_anh": img_base64,
                        "ket_qua": json.dumps([{"label": top_label, "confidence": top_prob}]),
                        "ten_san_pham": top_label,
                        "do_chinh_xac": top_prob,
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
                "confidence": top_prob
            })
            
            if top_prob > group_results[top_label]["confidence"]:
                group_results[top_label]["confidence"] = top_prob
            group_results[top_label]["count"] += 1
            group_results[top_label]["label"] = top_label

        grouped_results = sorted(
            [value for value in group_results.values()],
            key=lambda x: x["confidence"],
            reverse=True
        )
        
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
            "group_results": grouped_results,
            "thumbnails": thumbnails,
            "total_images": len(files)
        })
    except Exception as e:
        current_app.logger.error(f"Error processing multiple images: {e}")
        return jsonify({"error": f"Error processing images: {str(e)}"}), 500
