import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from config import TRAIN_DIR, TEST_DIR, IMG_SIZE, BATCH_SIZE
import os

# Kiểm tra thư mục dataset có tồn tại không
if not os.path.exists(TRAIN_DIR):
    raise ValueError(f"❌ Thư mục training không tồn tại: {TRAIN_DIR}")
if not os.path.exists(TEST_DIR):
    raise ValueError(f"❌ Thư mục test không tồn tại: {TEST_DIR}")

print(f"✅ Sử dụng dataset từ: {TRAIN_DIR} và {TEST_DIR}")
print(f"✅ Kích thước ảnh: {IMG_SIZE}")

# Tạo ImageDataGenerator với data augmentation mạnh hơn cho ảnh 128x128
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=30,  # Tăng rotation range
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.25,  # Tăng zoom range
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],  # Thêm brightness range
    channel_shift_range=0.1,  # Thêm channel shift
    fill_mode='nearest',  # Xác định cách điền giá trị khi rotate/shift
    validation_split=0.2  # Tách 20% dữ liệu training làm validation
)

# Chỉ rescale cho tập test, không augmentation
test_datagen = ImageDataGenerator(rescale=1.0 / 255)

# Tạo generator cho tập training
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',  # Chỉ định đây là tập training
    shuffle=True
)

# Tạo generator cho tập validation từ tập training
val_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',  # Chỉ định đây là tập validation
    shuffle=False
)

# Tạo generator cho tập test
test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# ✅ Lấy nhãn và số lớp tự động
CLASS_NAMES = list(train_generator.class_indices.keys())
NUM_CLASSES = train_generator.num_classes

print(f"✅ Đã load {NUM_CLASSES} lớp: {CLASS_NAMES}")
print(f"✅ Số lượng ảnh training: {train_generator.n}")
print(f"✅ Số lượng ảnh validation: {val_generator.n}")
print(f"✅ Số lượng ảnh test: {test_generator.n}")