from flask import Flask
import os
import logging
from datetime import timedelta
from routers.auth import auth_bp
from routers.main import main_bp
from routers.predict import predict_bp, init_app as init_predict
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
app.secret_key = os.getenv("SECRET_KEY") or "a-very-secret-key-for-development"

# Set session timeout to 1 day
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Force TensorFlow to use the CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Đăng ký các blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(admin_bp)

# Khởi tạo model cho blueprint predict
with app.app_context():
    init_predict(app)

# Make min and max functions available in templates
app.jinja_env.globals.update(max=max, min=min)

# Đăng ký filter formatdate
app.jinja_env.filters['formatdate'] = formatdate

# Đăng ký route cho login URL cụ thể
@app.route('/login')
def login():
    return auth_bp.login()

# Kiểm tra kết nối Supabase khi ứng dụng khởi động
def check_supabase_connection():
    try:
        supabase = get_supabase_client()
        logger.info("Kết nối Supabase thành công")
        
        # Kiểm tra cấu trúc bảng
        try:
            response = supabase.table('taikhoan').select('is_admin').limit(1).execute()
            logger.info("Cột is_admin tồn tại trong bảng taikhoan")
        except Exception as e:
            logger.error(f"Cột is_admin không tồn tại: {str(e)}")
    except Exception as e:
        logger.error(f"Không thể kết nối đến Supabase: {str(e)}")

# Kiểm tra kết nối khi khởi động
with app.app_context():
    check_supabase_connection()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)