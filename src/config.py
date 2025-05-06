import os

# Đường dẫn dataset
DATASET_PATH = os.path.abspath("dataset_vietnamese")
TRAIN_DIR = os.path.join(DATASET_PATH, "Training")
TEST_DIR = os.path.join(DATASET_PATH, "Test")

# Đường dẫn lưu mô hình
MODEL_SAVE_PATH = os.path.abspath(os.path.join("save_model", "best_model_2804.h5"))
CHECKPOINT_PATH = os.path.abspath(os.path.join("save_model", "fruit_model_2804.h5"))

# Tham số huấn luyện
IMG_SIZE = (100, 100)  # Kích thước ảnh đầu vào
BATCH_SIZE = 64  
LEARNING_RATE = 0.001
EPOCHS = 10
FINE_TUNE_EPOCHS = 10  # Fine-tune

# Lấy danh sách lớp từ dataset
try:
    CLASS_NAMES = sorted([d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))])
    NUM_CLASSES = len(CLASS_NAMES)
except FileNotFoundError:
    CLASS_NAMES = []
    NUM_CLASSES = 0

# Thông tin kết nối Supabase
SUPABASE_URL = "https://vplhqdnhnoggzboourea.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwbGhxZG5obm9nZ3pib291cmVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTg5MDI0MiwiZXhwIjoyMDYxNDY2MjQyfQ.gNz7bbiXzyeL6syYsSnOncpM_0rvw2yqJ0fjBAiKaRU"

# SERPAPI key
SERPAPI_KEY = "9b3dc8b422ca3f615511E6bfd04f15877c5f95945704a54f92ca1e627cd8058f6ecdb1b"