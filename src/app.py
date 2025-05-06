from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import logging
import base64
from supabase import create_client, Client
from config import IMG_SIZE, TRAIN_DIR, MODEL_SAVE_PATH, SUPABASE_URL, SUPABASE_ANON_KEY
import json
from datetime import datetime
import pytz

# Khởi tạo Flask, chỉ định thư mục chứa HTML và static files
app = Flask(__name__, 
            template_folder=os.path.abspath("frontend"),
            static_folder=os.path.abspath("frontend"))

# Configure secret key for session management
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Force TensorFlow to use the CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Load mô hình đã train
model = tf.keras.models.load_model(MODEL_SAVE_PATH)

# Lấy danh sách lớp từ thư mục dataset
class_names = sorted([d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))])

# Supabase connection
def get_supabase_client() -> Client:
    """Khởi tạo và trả về client kết nối Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def preprocess_image(image):
    """ Tiền xử lý ảnh đầu vào trước khi đưa vào mô hình """
    image = image.convert("RGB")
    image = image.resize((100, 100))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

from datetime import datetime
import pytz

# Thêm hàm chuyển đổi timezone
def convert_to_vietnam_time(utc_time):
    """Chuyển đổi từ UTC sang giờ Việt Nam (UTC+7)"""
    utc_tz = pytz.timezone('UTC')
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    if isinstance(utc_time, str):
        # Parse chuỗi thời gian
        try:
            dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S')
    else:
        dt = utc_time
    
    # Thêm thông tin timezone UTC
    dt_utc = utc_tz.localize(dt)
    # Chuyển sang giờ Việt Nam
    dt_vietnam = dt_utc.astimezone(vietnam_tz)
    
    return dt_vietnam

# Thêm filter để format thời gian
@app.template_filter('formatdate')
def formatdate(value, format='%d/%m/%Y %H:%M'):
    if isinstance(value, str):
        try:
            # Chuyển đổi sang giờ Việt Nam
            vietnam_time = convert_to_vietnam_time(value)
            return vietnam_time.strftime(format)
        except Exception as e:
            app.logger.error(f"Lỗi chuyển đổi thời gian: {e}")
            return value
    return value.strftime(format)

@app.template_filter('enumerate')
def _enumerate(seq):
    return enumerate(seq)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        supabase = get_supabase_client()
        response = supabase.table('taikhoan').select('id, taikhoan, Avarta, matkhau').eq('taikhoan', username).eq('matkhau', password).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            # DEBUG: In ra thông tin user và id kiểu
            app.logger.debug(f"User from database: {user}")
            app.logger.debug(f"User ID: {user['id']}")
            app.logger.debug(f"Type of user ID: {type(user['id'])}")

            session["user_id"] = user['id']
            # DEBUG: Kiểm tra giá trị session sau khi set
            app.logger.debug(f"Session user_id: {session['user_id']}")
            app.logger.debug(f"Type of session user_id: {type(session['user_id'])}")

            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Tên người dùng hoặc mật khẩu không hợp lệ !")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("logout"))
    
    user = response.data[0]
    return render_template("index.html", username=user['taikhoan'], avatar_url=user['Avarta'])

@app.route("/shop", methods=["GET"])
def shop():
    if "user_id" not in session:
        return redirect(url_for("login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("logout"))
    
    user = response.data[0]
    return render_template("shop.html", username=user['taikhoan'], avatar_url=user['Avarta'])

@app.route("/news", methods=["GET"])
def news():
    if "user_id" not in session:
        return redirect(url_for("login"))

    supabase = get_supabase_client()
    response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
    
    if not response.data or len(response.data) == 0:
        return redirect(url_for("logout"))
    
    user = response.data[0]
    return render_template("news.html", username=user['taikhoan'], avatar_url=user['Avarta'])

@app.route("/predict", methods=["POST"])
def predict():
    """ Xử lý ảnh tải lên và dự đoán loại hoa quả """
    if "file" not in request.files:
        app.logger.debug("No file part in the request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == '':
        app.logger.debug("No selected file")
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)

        # Chuyển ảnh thành base64 để hiển thị trên frontend
        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_base64 = "data:image/png;base64," + base64.b64encode(img_io.getvalue()).decode()

        # Dự đoán
        predictions = model.predict(processed_image)[0]
        top_5_indices = predictions.argsort()[-5:][::-1]
        top_5_labels = [class_names[idx] for idx in top_5_indices]
        top_5_probs = [float(predictions[idx]) for idx in top_5_indices]

        app.logger.debug(f"Top 5 Predictions: {list(zip(top_5_labels, top_5_probs))}")

        # Chuẩn bị kết quả
        prediction_results = []
        for label, conf in zip(top_5_labels, top_5_probs):
            prediction_results.append({"label": label, "confidence": conf})

        # Lưu lịch sử vào Supabase
        if "user_id" in session:
            try:
                # DEBUG: In ra user_id trước khi lưu
                app.logger.debug(f"Saving to history for user_id: {session['user_id']}")
                app.logger.debug(f"Type of user_id when saving: {type(session['user_id'])}")
                supabase = get_supabase_client()
                
                # Chuẩn bị dữ liệu lịch sử
                history_data = {
                    "user_id": session["user_id"],
                    "hinh_anh": img_base64,
                    "ket_qua": json.dumps(prediction_results),
                    "ten_san_pham": top_5_labels[0],
                    "do_chinh_xac": float(top_5_probs[0])
                }
                # DEBUG: In ra dữ liệu trước khi lưu
                app.logger.debug(f"History data to save: {history_data}")

                # Thêm vào bảng LichSuNhanDien
                response = supabase.table('lichsunhandien').insert(history_data).execute()
                app.logger.debug(f"Lịch sử lưu thành công: {response.data}")
                
            except Exception as e:
                app.logger.error(f"Lỗi khi lưu lịch sử: {e}")

        return jsonify({
            "image": img_base64,
            "predictions": prediction_results
        })
    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Error processing image"}), 500

@app.route("/history", methods=["GET"])
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        supabase = get_supabase_client()
        
        # DEBUG: In ra user_id hiện tại
        app.logger.debug(f"Current user_id in session: {session['user_id']}")
        app.logger.debug(f"Type of user_id: {type(session['user_id'])}")
        
        # Lấy thông tin user
        user_response = supabase.table('taikhoan').select('taikhoan, Avarta').eq('id', session["user_id"]).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            return redirect(url_for("logout"))
        
        user = user_response.data[0]
        
        # DEBUG: Kiểm tra việc truy vấn lịch sử
        app.logger.debug(f"Querying history for user_id: {session['user_id']}")
        
        # Lấy lịch sử nhận diện của user
        history_response = supabase.table('lichsunhandien')\
            .select('*')\
            .eq('user_id', int(session["user_id"]))\
            .order('thoi_gian', desc=True)\
            .limit(50)\
            .execute()
        
        # DEBUG: Kiểm tra kết quả truy vấn
        app.logger.debug(f"History query response: {history_response.data}")
        app.logger.debug(f"Number of history items: {len(history_response.data) if history_response.data else 0}")
        
        history_data = history_response.data if history_response.data else []
        
        # Xử lý dữ liệu trước khi gửi sang template
        for item in history_data:
            try:
                item['ket_qua'] = json.loads(item['ket_qua']) if isinstance(item['ket_qua'], str) else item['ket_qua']
            
                # Chuyển đổi thời gian sang giờ Việt Nam
                if 'thoi_gian' in item and isinstance(item['thoi_gian'], str):
                    vietnam_time = convert_to_vietnam_time(item['thoi_gian'])
                    item['thoi_gian'] = vietnam_time.strftime('%Y-%m-%d %H:%M:%S')
        
            except json.JSONDecodeError:
                app.logger.error(f"Lỗi parse JSON cho item {item['id']}")
                item['ket_qua'] = []
            except Exception as e:
                app.logger.error(f"Lỗi xử lý thời gian cho item {item['id']}: {str(e)}")
        
        return render_template("history.html", 
                             username=user['taikhoan'], 
                             avatar_url=user['Avarta'],
                             history=history_data)
                             
    except Exception as e:
        app.logger.error(f"Lỗi khi lấy lịch sử: {e}")
        return render_template("history.html", 
                             username="",
                             avatar_url="",
                             history=[],
                             error="Không thể tải lịch sử")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)