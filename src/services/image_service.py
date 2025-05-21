import numpy as np
from PIL import Image
import os
import json

def get_image_size():
    """Lấy kích thước ảnh từ cấu hình hệ thống"""
    try:
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'img_size' in config:
                    return tuple(config['img_size'])
    except Exception as e:
        print(f"Error loading image size from config: {str(e)}")
    
    # Default size if config not found or error
    from config import IMG_SIZE
    return IMG_SIZE

def preprocess_image(image):
    """ Tiền xử lý ảnh đầu vào trước khi đưa vào mô hình """
    image = image.convert("RGB")
    
    # Get the current image size configuration
    img_size = get_image_size()
    
    image = image.resize(img_size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image
