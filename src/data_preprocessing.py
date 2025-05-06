from keras.preprocessing.image import ImageDataGenerator
from config import TRAIN_DIR, TEST_DIR, IMG_SIZE, BATCH_SIZE

# ✅ Tăng cường dữ liệu tránh overfitting
data_augmentation = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=30,  # 🔄 Xoay tối đa 30 độ
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,  # ✅ Lật ngang nhưng KHÔNG lật dọc
    fill_mode="nearest",
    validation_split=0.2  # 📌 20% ảnh dùng làm validation
)

train_generator = data_augmentation.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True,
    subset="training"
)

val_generator = data_augmentation.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True,
    subset="validation"
)

test_generator = ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
    TEST_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)