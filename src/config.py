import os
from dotenv import load_dotenv

load_dotenv()  # Chỉ cần gọi 1 lần, tốt nhất là tại app khởi động

# Đường dẫn dataset
DATASET_PATH = os.path.abspath("dataset_vietnamese")
TRAIN_DIR = os.path.join(DATASET_PATH, "Training")
TEST_DIR = os.path.join(DATASET_PATH, "Test")

# Đường dẫn lưu mô hình
MODEL_SAVE_PATH = os.path.abspath(os.path.join("saved_model", "MobileNetV2_1905.h5"))

# Tham số huấn luyện - Đã tối ưu cho ảnh 128x128
IMG_SIZE = (128, 128)
BATCH_SIZE = 64
LEARNING_RATE = 0.001  # Tăng lên 0.001 cho giai đoạn feature extraction
FINE_TUNE_LR = 0.0001  # Learning rate thấp hơn cho fine-tuning
EPOCHS = 20  # Tăng số epochs
FINE_TUNE_EPOCHS = 15  # Tăng số epochs cho fine-tuning
FINE_TUNE_LAYERS = 50  # Số lớp mở khóa cho fine-tuning

# Tham số regularization
DROPOUT_RATE = 0.4  # Tăng dropout để giảm overfitting

# Mô hình
MODEL_TYPE = "MobileNetV2"
YOLO_MODEL_PATH = "yolo_model.onnx"
CONFIDENCE_THRESHOLD = 0.5

# Kết nối Supabase (từ biến môi trường)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3o-mini"  # Cho các tác vụ text cơ bản
OPENAI_VISION_MODEL = "gpt-4o-mini"  # Phiên bản tiết kiệm cho xử lý ảnh
OPENAI_MAX_TOKENS = 1800
OPENAI_TEMPERATURE = 0.7
TIMEOUT = 100.0
