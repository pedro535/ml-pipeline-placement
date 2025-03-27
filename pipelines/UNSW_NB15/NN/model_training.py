from mlopx.artifacts import InputDataset, OutputModel


def model_training(
    x_train_ds: InputDataset,
    y_train_ds: InputDataset,
    model_artifact: OutputModel
):
    
    import numpy as np
    import tensorflow as tf
    import keras

    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"


    # Load data
    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)

    # Define model
    input_shape = (x_train.shape[1],)
    n_classes = 2

    model = keras.Sequential([
        # input layer
        keras.layers.Input(shape=input_shape),
        # hidden layers
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(96, activation='relu'),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.25),
        # output layer
        keras.layers.Dense(n_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Model training
    with tf.device(device):
        model.fit(x_train, y_train, epochs=10, batch_size=32)

    # Save model
    model.save(model_artifact.path + "/model.h5")
    print(f"Model saved to {model_artifact.path}")
