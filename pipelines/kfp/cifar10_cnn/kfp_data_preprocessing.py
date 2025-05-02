from kfp import dsl
from kfp.dsl import Dataset, Output


@dsl.component(base_image="registry.localhost/kfp_tf_base:kfp")
def data_preprocessing(
    dataset_path: str,
    x_train_ds: Output[Dataset],
    x_test_ds: Output[Dataset],
    y_train_ds: Output[Dataset],
    y_test_ds: Output[Dataset],
):
    import numpy as np
    from sklearn.model_selection import train_test_split

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)

    x = np.load(f"{dataset_path}/x.npy")
    y = np.load(f"{dataset_path}/y.npy")
    x = x / 255.0
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=True, random_state=42
    )
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")
