from kfp import dsl
from kfp.dsl import Dataset, Output


@dsl.component(
    base_image="registry.localhost/python_kfp:v3"
)
def data_collection(
    dataset_path: str,
    X_train_ds: Output[Dataset],
    X_val_ds: Output[Dataset],
    X_test_ds: Output[Dataset],
    y_train_ds: Output[Dataset],
    y_val_ds: Output[Dataset],
    y_test_ds: Output[Dataset]
):
    import os
    import numpy as np
    import pandas as pd
    from PIL import Image
    from sklearn.model_selection import train_test_split
    from tensorflow.keras.utils import to_categorical

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)


    # Load train and validation data
    data = []
    labels = []
    classes = 43

    for i in range(classes):
        path = os.path.join(dataset_path, "Train", str(i))
        images = os.listdir(path)

        for a in images:
            try:
                image = Image.open(os.path.join(path, a))
                image = image.resize((30, 30))
                image = np.array(image) / 255
                data.append(image)
                labels.append(i)
            except Exception:
                print("Error loading image")

    data = np.array(data)
    labels = np.array(labels)

    X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=0.2, random_state=42)
    y_train = to_categorical(y_train, classes)
    y_val = to_categorical(y_val, classes)
    
    # Load test data
    test_details = pd.read_csv(f"{dataset_path}/Test.csv")

    data = []
    imgs = test_details["Path"].values
    labels = test_details["ClassId"].values

    for img in imgs:
        image = Image.open(f"{dataset_path}/{img}")
        image = image.resize([30, 30])
        image = np.array(image) / 255
        data.append(image)

    X_test = np.array(data)
    y_test = np.array(labels)

    # Save data as artifacts
    npy_save(X_train, X_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(X_val, X_val_ds.path)
    npy_save(y_val, y_val_ds.path)
    npy_save(X_test, X_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")