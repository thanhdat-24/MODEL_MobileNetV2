from keras.applications import MobileNetV2
from keras.models import Model
from keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from keras.optimizers import Adam
from config import IMG_SIZE, LEARNING_RATE, MODEL_TYPE
from data_preprocessing import NUM_CLASSES  # ✅ lấy từ data_preprocessing

def build_model():
    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(NUM_CLASSES, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE), loss="categorical_crossentropy", metrics=["accuracy"])
    return model

def fine_tune_model(model, unfreeze_layers=20, fine_tune_lr=LEARNING_RATE / 10):
    for layer in model.layers[-unfreeze_layers:]:
        if not isinstance(layer, BatchNormalization):
            layer.trainable = True

    model.compile(optimizer=Adam(learning_rate=fine_tune_lr), loss="categorical_crossentropy", metrics=["accuracy"])
    return model
