import tensorflow as tf
from keras.applications import MobileNetV2
from keras.models import Model
from keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras import mixed_precision
from config import IMG_SIZE, LEARNING_RATE, NUM_CLASSES, CHECKPOINT_PATH

# ✅ Bật mixed precision để tối ưu GPU
mixed_precision.set_global_policy('mixed_float16')

def build_model():
    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    base_model.trainable = False  # Đóng băng backbone

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation="relu")(x)  # 🔧 Tăng số neurons
    x = Dropout(0.4)(x)  # 🔧 Tăng Dropout để giảm overfitting
    output = Dense(NUM_CLASSES, activation="softmax", dtype="float32")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE), loss="categorical_crossentropy", metrics=["accuracy"])

    return model

def fine_tune_model(model, unfreeze_layers=50, fine_tune_lr=LEARNING_RATE / 20):
    """ Mở khóa nhiều lớp hơn để fine-tune """
    for layer in model.layers[-unfreeze_layers:]:
        if not isinstance(layer, BatchNormalization):
            layer.trainable = True  

    model.compile(optimizer=Adam(learning_rate=fine_tune_lr), loss="categorical_crossentropy", metrics=["accuracy"])
    return model

def get_checkpoint_callback():
    """ Trả về callback để lưu model tốt nhất """
    return ModelCheckpoint(CHECKPOINT_PATH, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)