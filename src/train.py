import tensorflow as tf
from model import build_model, fine_tune_model, get_checkpoint_callback
from data_preprocessing import train_generator, val_generator, test_generator
from config import EPOCHS, FINE_TUNE_EPOCHS, MODEL_SAVE_PATH

# Kiểm tra GPU
gpu_devices = tf.config.list_physical_devices('GPU')
if gpu_devices:
    print("✅ Đang sử dụng GPU")
    for gpu in gpu_devices:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("⚠️ Không tìm thấy GPU, sẽ train bằng CPU")

# 🚀 Xây dựng mô hình
model = build_model()

# 🏋️ Huấn luyện giai đoạn 1 (Freeze backbone)
print("🚀 Bắt đầu huấn luyện giai đoạn 1...")
history = model.fit(train_generator, validation_data=val_generator, epochs=EPOCHS, callbacks=[get_checkpoint_callback()])

# ✅ Lưu mô hình cuối cùng
model.save_weights(MODEL_SAVE_PATH)
print(f"✅ Trọng số mô hình đã lưu tại {MODEL_SAVE_PATH}")

# 🔥 Fine-tuning (Mở khóa 50 lớp cuối cùng)
print("\n🔧 Bắt đầu Fine-tuning mô hình...")
model = fine_tune_model(model, unfreeze_layers=50)

# 🏋️ Huấn luyện giai đoạn 2 (Fine-tune)
history_fine = model.fit(train_generator, validation_data=val_generator, epochs=FINE_TUNE_EPOCHS, callbacks=[get_checkpoint_callback()])

# ✅ Lưu trọng số sau Fine-tuning
model.save_weights(MODEL_SAVE_PATH)
print(f"✅ Model đã lưu sau Fine-tuning tại {MODEL_SAVE_PATH}")