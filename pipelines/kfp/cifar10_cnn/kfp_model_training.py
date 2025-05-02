from kfp import dsl
from kfp.dsl import Dataset, Model, Input, Output


@dsl.component(base_image="registry.localhost/kfp_tf_base:kfp")
def model_training(
    x_train_ds: Input[Dataset],
    y_train_ds: Input[Dataset],
    model_artifact: Output[Model],
):
    import numpy as np
    import tensorflow as tf
    import keras
    import random

    seed = 42
    tf.random.set_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"
    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)
    input_shape = 32, 32, 3
    n_classes = 10
    model = keras.Sequential(
        [
            keras.layers.Conv2D(
                32, (3, 3), activation="relu", padding="same", input_shape=input_shape
            ),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(n_classes, activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )
    with tf.device(device):
        model.fit(x_train, y_train, epochs=5, batch_size=64)
    model.save(model_artifact.path + "/model.h5")
    print(f"Model saved to {model_artifact.path}")
