import os
from dotenv import load_dotenv

load_dotenv()  # Chỉ cần gọi 1 lần, tốt nhất là tại app khởi động

# Đường dẫn dataset
DATASET_PATH = os.path.abspath("dataset_vietnamese")
TRAIN_DIR = os.path.join(DATASET_PATH, "Training")
TEST_DIR = os.path.join(DATASET_PATH, "Test")

# Đường dẫn lưu mô hình
MODEL_SAVE_PATH = os.path.abspath(os.path.join("saved_model", "best_model_2804.h5"))

# Tham số huấn luyệnS
IMG_SIZE = (100, 100)
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 10
FINE_TUNE_EPOCHS = 10

# Mô hình
MODEL_TYPE = "MobileNetV2"
YOLO_MODEL_PATH = "yolo_model.onnx"
CONFIDENCE_THRESHOLD = 0.5

# Kết nối Supabase (từ biến môi trường)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1800
OPENAI_TEMPERATURE = 0.7
TIMEOUT = 100.0
