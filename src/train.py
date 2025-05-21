import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import os
import multiprocessing
from model import build_model, fine_tune_model
from data_preprocessing import train_generator, val_generator, test_generator, CLASS_NAMES, NUM_CLASSES
from config import EPOCHS, FINE_TUNE_EPOCHS, MODEL_SAVE_PATH, MODEL_TYPE, IMG_SIZE, BATCH_SIZE, FINE_TUNE_LAYERS
from keras.callbacks import EarlyStopping, ModelCheckpoint, CSVLogger, ReduceLROnPlateau, TensorBoard
from datetime import datetime

# ✅ Sử dụng GPU nếu có
def setup_gpu():
    gpu_devices = tf.config.list_physical_devices('GPU')
    if gpu_devices:
        print("✅ Sử dụng GPU để train")
        for gpu in gpu_devices:
            tf.config.experimental.set_memory_growth(gpu, True)
    else:
        print("⚠️ Không tìm thấy GPU, sẽ train bằng CPU")

# Hàm chính để huấn luyện mô hình
def train_model():
    # Tạo thư mục plots và logs nếu chưa có
    os.makedirs("plots", exist_ok=True)
    log_dir = os.path.join("logs", datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(log_dir, exist_ok=True)

    # ✅ Callbacks nâng cao để tối ưu hóa quá trình huấn luyện
    callbacks = [
        # Dừng sớm khi mô hình không cải thiện
        EarlyStopping(
            monitor='val_loss', 
            patience=10,  # Tăng patience lên 10
            restore_best_weights=True,
            verbose=1
        ),
        # Lưu mô hình tốt nhất
        ModelCheckpoint(
            MODEL_SAVE_PATH, 
            save_best_only=True, 
            save_format='h5',
            verbose=1
        ),
        # Tự động giảm learning rate khi không cải thiện
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        # Lưu lịch sử huấn luyện
        CSVLogger('training_log.csv'),
        # Thêm TensorBoard để có thể theo dõi quá trình huấn luyện
        TensorBoard(log_dir=log_dir, histogram_freq=1)
    ]

    print(f"👉 Bắt đầu huấn luyện MobileNetV2 với {NUM_CLASSES} lớp thực phẩm")
    print(f"👉 Kích thước ảnh: {IMG_SIZE}, Batch size: {BATCH_SIZE}")

    # 🚀 Huấn luyện giai đoạn 1 - Feature extraction
    model, base_model = build_model()  # Lấy cả model và base_model
    print("🚀 Bắt đầu huấn luyện mô hình giai đoạn 1 (Feature Extraction)...")
    print(f"👉 Số epochs: {EPOCHS}")

    # Hiển thị thông tin mô hình
    model.summary()

    # Xác định liệu có nên sử dụng multiprocessing hay không (tránh trên Windows)
    use_mp = False if os.name == 'nt' else True
    workers = 1 if os.name == 'nt' else 4
    
    if not use_mp:
        print("⚠️ Không sử dụng multiprocessing trên Windows để tránh lỗi")
    
    history = model.fit(
        train_generator, 
        validation_data=val_generator,  # Sử dụng validation generator
        epochs=EPOCHS, 
        callbacks=callbacks,
        verbose=1,
        workers=workers,  # Giảm số worker trên Windows
        use_multiprocessing=use_mp  # Tắt multiprocessing trên Windows
    )

    # Lưu lịch sử training phase 1
    history_dict = {k: [float(x) for x in v] for k, v in history.history.items()}
    df_history = pd.DataFrame(history_dict)
    df_history.to_csv('train_history_phase1.csv', index=False, encoding='utf-8-sig')
    print("✅ Đã lưu lịch sử train phase 1 ra file train_history_phase1.csv")

    print(f"✅ Mô hình đã lưu tại {MODEL_SAVE_PATH}")

    # 🔧 Fine-tune giai đoạn 2
    print("\n🔧 Bắt đầu Fine-tuning mô hình...")
    print(f"👉 Số epochs fine-tuning: {FINE_TUNE_EPOCHS}")
    print(f"👉 Số lớp được mở khóa: {FINE_TUNE_LAYERS}")

    model = fine_tune_model(model, base_model, unfreeze_layers=FINE_TUNE_LAYERS)
    history_fine = model.fit(
        train_generator, 
        validation_data=val_generator,  # Sử dụng validation generator 
        epochs=FINE_TUNE_EPOCHS, 
        callbacks=callbacks,
        verbose=1,
        workers=workers,  # Giảm số worker trên Windows
        use_multiprocessing=use_mp  # Tắt multiprocessing trên Windows
    )

    # Lưu lịch sử fine-tuning
    history_fine_dict = {k: [float(x) for x in v] for k, v in history_fine.history.items()}
    df_history_fine = pd.DataFrame(history_fine_dict)
    df_history_fine.to_csv('train_history_finetune.csv', index=False, encoding='utf-8-sig')
    print("✅ Đã lưu lịch sử train fine-tune ra file train_history_finetune.csv")

    print(f"✅ Mô hình đã lưu sau Fine-tuning tại {MODEL_SAVE_PATH}")

    # 🔽 Gọi hàm vẽ biểu đồ và đánh giá mô hình
    plot_training_curves(history, history_fine)
    evaluate_model(model, test_generator)

# Hàm vẽ biểu đồ training curves
def plot_training_curves(history, history_fine, save_dir="plots"):
    plt.figure(figsize=(14, 6))
    plt.suptitle(f"Training Curves for {MODEL_TYPE}", fontsize=16)

    # Subplot 1: Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy (Phase 1)')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy (Phase 1)')
    if history_fine and len(history_fine.history['accuracy']) > 0:
        # Nối kết quả từ phase 1 và fine-tuning để có biểu đồ liên tục
        plt.plot(range(len(history.history['accuracy']), 
                     len(history.history['accuracy']) + len(history_fine.history['accuracy'])),
                     history_fine.history['accuracy'], 
                     label='Train Accuracy (Fine-tune)')
        plt.plot(range(len(history.history['val_accuracy']), 
                     len(history.history['val_accuracy']) + len(history_fine.history['val_accuracy'])),
                     history_fine.history['val_accuracy'], 
                     label='Val Accuracy (Fine-tune)')
    plt.title('Accuracy qua từng epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    # Subplot 2: Loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss (Phase 1)')
    plt.plot(history.history['val_loss'], label='Val Loss (Phase 1)')
    if history_fine and len(history_fine.history['loss']) > 0:
        # Nối kết quả từ phase 1 và fine-tuning để có biểu đồ liên tục
        plt.plot(range(len(history.history['loss']), 
                     len(history.history['loss']) + len(history_fine.history['loss'])),
                     history_fine.history['loss'], 
                     label='Train Loss (Fine-tune)')
        plt.plot(range(len(history.history['val_loss']), 
                     len(history.history['val_loss']) + len(history_fine.history['val_loss'])),
                     history_fine.history['val_loss'], 
                     label='Val Loss (Fine-tune)')
    plt.title('Loss qua từng epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    # Lưu biểu đồ
    save_path = os.path.join(save_dir, "training_curves_combined.png")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"📊 Đã lưu biểu đồ tổng hợp tại: {save_path}")
    plt.close()
    
    # Vẽ thêm biểu đồ Learning Rate (nếu có)
    if 'lr' in history.history:
        plt.figure(figsize=(10, 6))
        lr_data = history.history['lr']
        if history_fine and 'lr' in history_fine.history:
            lr_data.extend(history_fine.history['lr'])
        plt.plot(lr_data)
        plt.title('Learning Rate')
        plt.xlabel('Epoch')
        plt.ylabel('Learning Rate')
        plt.yscale('log')
        plt.grid(True)
        save_path = os.path.join(save_dir, "learning_rate.png")
        plt.savefig(save_path)
        plt.close()
        print(f"📊 Đã lưu biểu đồ learning rate tại: {save_path}")

# Hàm đánh giá mô hình
def evaluate_model(model, test_generator, save_dir="plots"):
    # Đánh giá mô hình
    print("\n📊 Đánh giá mô hình trên tập test...")
    test_loss, test_acc = model.evaluate(test_generator, verbose=1)
    print(f"Test Accuracy: {test_acc:.4f}, Test Loss: {test_loss:.4f}")
    
    # Lưu kết quả chính vào file
    with open('final_results.txt', 'w') as f:
        f.write(f"Test Accuracy: {test_acc:.4f}\n")
        f.write(f"Test Loss: {test_loss:.4f}\n")
        f.write(f"Mô hình: {MODEL_TYPE}\n")
        f.write(f"Kích thước ảnh: {IMG_SIZE}\n")
        f.write(f"Số lớp: {NUM_CLASSES}\n")
    
    # Lấy confusion matrix và class_labels
    y_true = test_generator.classes
    class_labels = list(test_generator.class_indices.keys())
    
    # Tạo dự đoán
    print("🔍 Tạo dự đoán cho tập test...")
    y_pred_probs = model.predict(test_generator)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    # Tạo confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Xuất confusion matrix ra file CSV
    df_cm = pd.DataFrame(cm, index=class_labels, columns=class_labels)
    df_cm.to_csv('confusion_matrix_full.csv', encoding='utf-8-sig')
    print("✅ Đã lưu confusion matrix ra file confusion_matrix_full.csv")

    # Lọc ra các lớp bị nhầm nhiều nhất
    mistakes = np.sum(cm, axis=1) - np.diag(cm)
    df_mistakes = pd.DataFrame({
        'class': class_labels,
        'mistakes': mistakes
    })
    df_mistakes = df_mistakes.sort_values(by='mistakes', ascending=False)
    df_mistakes.to_csv('top_mistake_classes.csv', index=False, encoding='utf-8-sig')
    print("✅ Đã lưu top lớp bị nhầm nhiều nhất ra file top_mistake_classes.csv")

    # Lọc ra các cặp lớp bị nhầm nhiều nhất
    mistake_pairs = []
    for i in range(len(class_labels)):
        for j in range(len(class_labels)):
            if i != j and cm[i, j] > 0:
                mistake_pairs.append((class_labels[i], class_labels[j], cm[i, j]))
    mistake_pairs = sorted(mistake_pairs, key=lambda x: x[2], reverse=True)
    df_pairs = pd.DataFrame(mistake_pairs, columns=['Thực tế', 'Dự đoán', 'Số lần nhầm'])
    df_pairs.to_csv('top_mistake_pairs.csv', index=False, encoding='utf-8-sig')
    print("✅ Đã lưu top cặp lớp bị nhầm nhiều nhất ra file top_mistake_pairs.csv")

    # Vẽ lại confusion matrix cho top 10 lớp bị nhầm nhiều nhất
    top_n = min(10, len(df_mistakes))
    top_classes_idx = [list(class_labels).index(c) for c in df_mistakes.head(top_n)['class']]
    cm_sub = cm[top_classes_idx, :][:, top_classes_idx]
    labels_sub = [class_labels[i] for i in top_classes_idx]

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_sub, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels_sub, yticklabels=labels_sub)
    plt.xlabel('Dự đoán')
    plt.ylabel('Thực tế')
    plt.title(f'Ma trận nhầm lẫn cho {top_n} lớp bị nhầm nhiều nhất')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'confusion_matrix_top10.png'))
    print(f"✅ Đã lưu ma trận nhầm lẫn cho top {top_n} lớp bị nhầm nhiều nhất ra file {os.path.join(save_dir, 'confusion_matrix_top10.png')}")
    plt.close()

    # Xuất báo cáo phân loại
    report = classification_report(y_true, y_pred, target_names=class_labels, output_dict=True)
    df_report = pd.DataFrame(report).transpose()
    df_report.to_csv('classification_report.csv', encoding='utf-8-sig')
    print("✅ Đã lưu báo cáo phân loại ra file classification_report.csv")

# Điểm vào chính khi chạy script
if __name__ == "__main__":
    # Cần thiết cho multiprocessing trên Windows
    multiprocessing.freeze_support()
    
    # Thiết lập GPU
    setup_gpu()
    
    # Chạy quá trình huấn luyện
    train_model()