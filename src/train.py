import tensorflow as tf
from model import build_model, fine_tune_model
from data_preprocessing import train_generator, test_generator
from config import EPOCHS, FINE_TUNE_EPOCHS, MODEL_SAVE_PATH

from keras.callbacks import EarlyStopping, ModelCheckpoint

# ✅ Sử dụng GPU nếu có
gpu_devices = tf.config.list_physical_devices('GPU')
if gpu_devices:
    print("✅ Sử dụng GPU để train")
    for gpu in gpu_devices:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("⚠️ Không tìm thấy GPU, sẽ train bằng CPU")

# ✅ Callbacks để lưu mô hình tốt nhất
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True)
]

# 🚀 Huấn luyện giai đoạn 1
model = build_model()
print("🚀 Bắt đầu huấn luyện mô hình giai đoạn 1...")
history = model.fit(train_generator, validation_data=test_generator, epochs=EPOCHS, callbacks=callbacks)

print(f"✅ Mô hình đã lưu tại {MODEL_SAVE_PATH}")

# 🔧 Fine-tune giai đoạn 2
print("\n🔧 Bắt đầu Fine-tuning mô hình...")
model = fine_tune_model(model, unfreeze_layers=20)
history_fine = model.fit(train_generator, validation_data=test_generator, epochs=FINE_TUNE_EPOCHS, callbacks=callbacks)

print(f"✅ Mô hình đã lưu sau Fine-tuning tại {MODEL_SAVE_PATH}")