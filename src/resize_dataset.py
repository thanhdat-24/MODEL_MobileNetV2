import os
from PIL import Image
import glob

def resize_dataset(dataset_dir, target_size=(128, 128)):
    """Resize lại tất cả ảnh trong dataset về kích thước mới"""
    
    # Duyệt qua từng thư mục lớp
    for class_name in os.listdir(dataset_dir):
        class_path = os.path.join(dataset_dir, class_name)
        if not os.path.isdir(class_path):
            continue
            
        print(f"Đang xử lý thư mục: {class_name}")
        
        # Duyệt qua từng ảnh
        image_files = glob.glob(os.path.join(class_path, "*.jpg")) + \
                     glob.glob(os.path.join(class_path, "*.jpeg")) + \
                     glob.glob(os.path.join(class_path, "*.png"))
        
        for img_path in image_files:
            try:
                img = Image.open(img_path).convert('RGB')
                if img.size != target_size:
                    img_resized = img.resize(target_size, Image.LANCZOS)
                    img_resized.save(img_path, quality=95)
            except Exception as e:
                print(f"Lỗi xử lý ảnh {img_path}: {e}")

# Sử dụng hàm
print("Đang resize dataset Training...")
resize_dataset("dataset_vietnamese/Training", target_size=(128, 128))

print("Đang resize dataset Test...")
resize_dataset("dataset_vietnamese/Test", target_size=(128, 128))