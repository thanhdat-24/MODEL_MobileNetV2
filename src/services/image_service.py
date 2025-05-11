import numpy as np
from PIL import Image

def preprocess_image(image):
    """ Tiền xử lý ảnh đầu vào trước khi đưa vào mô hình """
    image = image.convert("RGB")
    image = image.resize((100, 100))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image
