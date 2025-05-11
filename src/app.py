from flask import Flask
import os
import logging
from routers.auth import auth_bp
from routers.main import main_bp
from routers.predict import predict_bp
from routers.history import history_bp
from routers.recipes import recipes_bp
from routers.admin import admin_bp
from services.supabase_service import get_supabase_client
from filters import formatdate
from dotenv import load_dotenv

# Khởi tạo Flask
app = Flask(__name__, 
            template_folder=os.path.abspath("frontend"),
            static_folder=os.path.abspath("frontend"))

# Configure secret key for session management
load_dotenv()  # Load environment variables from .env file
app.secret_key = os.getenv("SECRET_KEY")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Force TensorFlow to use the CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Đăng ký các blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(admin_bp)

# Kiểm tra kết nối Supabase khi ứng dụng khởi động
def check_supabase_connection():
    try:
        get_supabase_client()
        app.logger.info("Kết nối Supabase thành công")
    except Exception as e:
        app.logger.error(f"Không thể kết nối đến Supabase: {str(e)}")

# Kiểm tra kết nối khi khởi động
with app.app_context():
    check_supabase_connection()

# Đăng ký filter formatdate
app.jinja_env.filters['formatdate'] = formatdate

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)