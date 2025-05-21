import os
from PIL import Image
from collections import Counter

# Đường dẫn dataset
DATASET_PATH = os.path.abspath("dataset_vietnamese(128x128)")
TRAIN_DIR = os.path.join(DATASET_PATH, "Training")
TEST_DIR = os.path.join(DATASET_PATH, "Test")

def count_classes_and_images(folder_path):
    total_classes = 0
    total_images = 0

    # Duyệt từng thư mục con (tương ứng với mỗi class)
    for class_name in os.listdir(folder_path):
        class_path = os.path.join(folder_path, class_name)
        if os.path.isdir(class_path):
            total_classes += 1
            image_files = [f for f in os.listdir(class_path)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            total_images += len(image_files)

    return total_classes, total_images

# Thống kê Training
train_classes, train_images = count_classes_and_images(TRAIN_DIR)
print(f"[Training] Số lớp: {train_classes}, Số ảnh: {train_images}")

# Thống kê Test
test_classes, test_images = count_classes_and_images(TEST_DIR)
print(f"[Test] Số lớp: {test_classes}, Số ảnh: {test_images}")

# Tổng hợp
total_classes = len(set(os.listdir(TRAIN_DIR)) | set(os.listdir(TEST_DIR)))
total_images = train_images + test_images
print(f"[Tổng] Số lớp duy nhất: {total_classes}, Tổng ảnh: {total_images}")

from collections import Counter

def get_image_sizes(folder_path):
    size_counter = Counter()

    for class_name in os.listdir(folder_path):
        class_path = os.path.join(folder_path, class_name)
        if os.path.isdir(class_path):
            for filename in os.listdir(class_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(class_path, filename)
                    try:
                        with Image.open(img_path) as img:
                            size_counter[img.size] += 1  # (width, height)
                    except Exception as e:
                        print(f"Lỗi khi mở ảnh: {img_path} - {e}")
    
    return size_counter

# Thống kê kích thước ảnh
train_sizes = get_image_sizes(TRAIN_DIR)
test_sizes = get_image_sizes(TEST_DIR)

print("\n[Kích thước ảnh - Training]")
for size, count in train_sizes.items():
    print(f"Kích thước {size}: {count} ảnh")

print("\n[Kích thước ảnh - Test]")
for size, count in test_sizes.items():
    print(f"Kích thước {size}: {count} ảnh")
