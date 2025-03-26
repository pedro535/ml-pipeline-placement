from mlopx.artifacts import InputDataset, OutputModel


def model_training(
    x_train_ds: InputDataset,
    y_train_ds: InputDataset,
    model_artifact: OutputModel
):
    
    import numpy as np
    import tensorflow as tf
    import keras
    from keras import layers

    device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"


    # Load data
    x_train = np.load(x_train_ds.path)
    y_train = np.load(y_train_ds.path)

    # Define the model
    input_shape = (32, 32, 3)
    n_classes = 10
    
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        layers.Flatten(),
        layers.Dense(1024, activation=layers.LeakyReLU()),
        layers.Dense(512, activation=layers.LeakyReLU()),
        layers.Dense(n_classes, activation='softmax')
    ])

    # Compile the model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Train the model
    with tf.device(device):
        model.fit(x_train, y_train, epochs=10, batch_size=64)

    # Save model
    model.save(model_artifact.path + "/model.h5")
    print(f"Model saved to {model_artifact.path}")
