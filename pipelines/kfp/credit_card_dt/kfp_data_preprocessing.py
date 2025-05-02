from kfp import dsl
from kfp.dsl import Dataset, Output


@dsl.component(base_image="registry.localhost/kfp_python_base:kfp")
def data_preprocessing(
    dataset_path: str,
    x_train_ds: Output[Dataset],
    x_test_ds: Output[Dataset],
    y_train_ds: Output[Dataset],
    y_test_ds: Output[Dataset],
):
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)

    df = pd.read_csv(dataset_path)
    df = df.rename(columns={"default.payment.next.month": "default"})
    x = df.drop(columns=["ID", "default"])
    y = df["default"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")
