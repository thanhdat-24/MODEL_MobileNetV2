from keras.applications import MobileNetV2
from keras.models import Model
from keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from keras.optimizers import Adam
from config import IMG_SIZE, LEARNING_RATE, MODEL_TYPE, DROPOUT_RATE, FINE_TUNE_LAYERS, FINE_TUNE_LR
from data_preprocessing import NUM_CLASSES  # ✅ lấy từ data_preprocessing

def build_model():
    # Sử dụng pretrained MobileNetV2 làm base model
    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    base_model.trainable = False  # Đóng băng tất cả các lớp của base model ở giai đoạn 1

    # Xây dựng mô hình với kiến trúc phức tạp hơn để tận dụng ảnh 128x128
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    
    # Thêm lớp dense đầu tiên với nhiều node hơn
    x = Dense(256, activation="relu")(x)
    x = BatchNormalization()(x)
    x = Dropout(DROPOUT_RATE)(x)
    
    # Thêm lớp dense thứ hai
    x = Dense(128, activation="relu")(x)
    x = BatchNormalization()(x)
    x = Dropout(DROPOUT_RATE)(x)
    
    # Lớp output
    output = Dense(NUM_CLASSES, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)
    
    # Compile mô hình
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE), 
        loss="categorical_crossentropy", 
        metrics=["accuracy"]
    )
    
    return model, base_model

def fine_tune_model(model, base_model=None, unfreeze_layers=FINE_TUNE_LAYERS, fine_tune_lr=FINE_TUNE_LR):
    """
    Fine-tune model bằng cách mở khóa một số lớp cuối của base model.
    
    Args:
        model: Mô hình đã được huấn luyện ở giai đoạn 1
        base_model: Base model (MobileNetV2)
        unfreeze_layers: Số lớp cần mở khóa cho fine-tuning (từ cuối lên)
        fine_tune_lr: Learning rate cho fine-tuning (thường nhỏ hơn learning rate ban đầu)
    
    Returns:
        model: Mô hình đã được cấu hình lại cho fine-tuning
    """
    print(f"👉 Fine-tuning mô hình với {unfreeze_layers} lớp cuối được mở khóa")
    print(f"👉 Learning rate cho fine-tuning: {fine_tune_lr}")
    
    # Mở khóa các lớp cuối của base model
    if base_model:
        # Đóng băng tất cả các lớp
        base_model.trainable = True
        
        # Đóng băng các lớp đầu, chỉ mở các lớp cuối
        for layer in base_model.layers[:-unfreeze_layers]:
            layer.trainable = False
            
        # Hiển thị số lớp trainable và non-trainable
        trainable_count = sum(1 for layer in base_model.layers if layer.trainable)
        non_trainable_count = sum(1 for layer in base_model.layers if not layer.trainable)
        print(f"✅ Base model: {trainable_count} lớp trainable, {non_trainable_count} lớp non-trainable")
    else:
        # Fallback nếu không có base_model
        for layer in model.layers[-unfreeze_layers:]:
            if not isinstance(layer, BatchNormalization):
                layer.trainable = True

    # Compile lại mô hình với learning rate thấp hơn
    model.compile(
        optimizer=Adam(learning_rate=fine_tune_lr), 
        loss="categorical_crossentropy", 
        metrics=["accuracy"]
    )
    
    return model