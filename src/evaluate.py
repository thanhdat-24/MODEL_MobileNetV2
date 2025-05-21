# src/evaluate.py
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import pandas as pd
import config
from keras.preprocessing.image import ImageDataGenerator
import os

# 1. Load mô hình đã train
model = load_model(config.MODEL_SAVE_PATH)

# 2. Tạo test_generator
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    config.TEST_DIR,
    target_size=config.IMG_SIZE,
    batch_size=config.BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)
class_labels = list(test_generator.class_indices.keys())

# 3. Đánh giá accuracy trên tập test
test_loss, test_acc = model.evaluate(test_generator)
print(f"Test accuracy: {test_acc:.4f}")

# 4. Dự đoán trên tập test
y_true = test_generator.classes
y_pred_probs = model.predict(test_generator)
y_pred = np.argmax(y_pred_probs, axis=1)

# Tạo thư mục lưu kết quả nếu chưa có
save_dir = "test_diagram"
os.makedirs(save_dir, exist_ok=True)

# 5. Xuất confusion matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=False, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.tight_layout()
plt.savefig(os.path.join(save_dir, 'confusion_matrix.png'))
plt.close()
print(f"Đã lưu {os.path.join(save_dir, 'confusion_matrix.png')}")

# 6. Xuất classification report
report = classification_report(y_true, y_pred, target_names=class_labels, output_dict=True)
df_report = pd.DataFrame(report).transpose()
df_report.to_csv(os.path.join(save_dir, 'classification_report.csv'), encoding='utf-8-sig')
print(f"Đã lưu {os.path.join(save_dir, 'classification_report.csv')}")

# 7. Hiển thị một số ảnh dự đoán mẫu
def show_prediction_samples_all(test_generator, y_pred, num_samples=12):
    # Lấy toàn bộ dữ liệu test
    x_all = []
    y_all = []
    for i in range(len(test_generator)):
        x, y = test_generator[i]
        x_all.append(x)
        y_all.append(y)
    x_all = np.concatenate(x_all)
    y_all = np.concatenate(y_all)
    y_true_all = np.argmax(y_all, axis=1)

    # Lấy ngẫu nhiên num_samples chỉ số
    idxs = np.random.choice(len(x_all), size=num_samples, replace=False)
    plt.figure(figsize=(15, 8))
    for i, idx in enumerate(idxs):
        plt.subplot(3, 4, i+1)
        plt.imshow(x_all[idx])
        plt.axis('off')
        true_label = class_labels[y_true_all[idx]]
        pred_label = class_labels[y_pred[idx]]
        color = 'green' if y_true_all[idx] == y_pred[idx] else 'red'
        plt.title(f"GT: {true_label}\nPred: {pred_label}", color=color)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'sample_predictions.png'))
    plt.close()
    print(f"Đã lưu {os.path.join(save_dir, 'sample_predictions.png')}")

show_prediction_samples_all(test_generator, y_pred)

# 8. Hiển thị một số ảnh bị dự đoán sai
def show_misclassified_samples(test_generator, y_pred, num_samples=12):
    x_test, y_test = next(test_generator)
    y_true = np.argmax(y_test, axis=1)
    mis_idx = np.where(y_pred != y_true)[0]
    plt.figure(figsize=(15, 8))
    for i, idx in enumerate(mis_idx[:num_samples]):
        plt.subplot(3, 4, i+1)
        plt.imshow(x_test[idx])
        plt.axis('off')
        true_label = class_labels[y_true[idx]]
        pred_label = class_labels[y_pred[idx]]
        plt.title(f"GT: {true_label}\nPred: {pred_label}", color='red')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'misclassified_samples.png'))
    plt.close()
    print(f"Đã lưu {os.path.join(save_dir, 'misclassified_samples.png')}")

show_misclassified_samples(test_generator, y_pred)

print("✅ Đánh giá hoàn tất. Xem các file trong thư mục test_diagram để đưa vào báo cáo.")