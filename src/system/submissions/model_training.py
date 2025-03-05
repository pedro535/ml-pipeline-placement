#### For development purposes only ####
import sys
sys.path.append("../../")
#######################################

from src.pipeline.artifacts import InputDataset, OutputModel


def model_training(
    X_train_ds: InputDataset,
    X_val_ds: InputDataset,
    y_train_ds: InputDataset,
    y_val_ds: InputDataset,
    model_artifact: OutputModel,
    epochs: int,
    batch_size: int
):
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Input, Conv2D, MaxPool2D, Dense, Flatten, Dropout
    
    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"


    # Load data
    X_train = np.load(X_train_ds.path)
    X_val = np.load(X_val_ds.path)
    y_train = np.load(y_train_ds.path)
    y_val = np.load(y_val_ds.path)

    #  Build model
    model = Sequential([
        Input(shape=(X_train.shape[1:])),
        Conv2D(filters=32, kernel_size=(5, 5), activation="relu"),
        Conv2D(filters=64, kernel_size=(5, 5), activation="relu"),
        MaxPool2D(pool_size=(2, 2)),
        Dropout(rate=0.15),
        Conv2D(filters=128, kernel_size=(3, 3), activation="relu"),
        Conv2D(filters=256, kernel_size=(3, 3), activation="relu"),
        MaxPool2D(pool_size=(2, 2)),
        Dropout(rate=0.20),
        Flatten(),
        Dense(512, activation="relu"),
        Dropout(rate=0.25),
        Dense(43, activation="softmax")
    ])

    model.compile(
        loss = "categorical_crossentropy",
        optimizer = "adam",
        metrics = ["accuracy"]
    )
    
    # Train Model
    with tf.device(device):
        model.fit(
            X_train,
            y_train,
            batch_size = batch_size,
            epochs = epochs,
            validation_data = (X_val, y_val),
            verbose = 2
        )

    # Save model
    model.save(model_artifact.path + "/model.h5")
    print(f"Model saved to {model_artifact.path}")
