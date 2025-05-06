import os

# Đường dẫn dataset
DATASET_PATH = os.path.abspath("dataset_vietnamese")
TRAIN_DIR = os.path.join(DATASET_PATH, "Training")
TEST_DIR = os.path.join(DATASET_PATH, "Test")

# Đường dẫn lưu mô hình
MODEL_SAVE_PATH = os.path.abspath(os.path.join("saved_model", "best_model_2804.h5"))

# Tham số huấn luyện
IMG_SIZE = (100, 100)
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 10
FINE_TUNE_EPOCHS = 10

# Lưu ý: Không tính NUM_CLASSES ở đây nữa, chuyển sang lấy từ data_preprocessing

# Kiểu mô hình backbone
MODEL_TYPE = "MobileNetV2"

# Cấu hình YOLO nếu cần
YOLO_MODEL_PATH = "yolo_model.onnx"
CONFIDENCE_THRESHOLD = 0.5

# Thông tin kết nối Supabase
SUPABASE_URL = "https://vplhqdnhnoggzboourea.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwbGhxZG5obm9nZ3pib291cmVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTg5MDI0MiwiZXhwIjoyMDYxNDY2MjQyfQ.gNz7bbiXzyeL6syYsSnOncpM_0rvw2yqJ0fjBAiKaRU"
