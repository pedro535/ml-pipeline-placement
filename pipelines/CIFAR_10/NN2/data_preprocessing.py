from mlopx.pipelines.artifacts import OutputDataset


def data_preprocessing(
    dataset_path: str,
    x_train_ds: OutputDataset,
    x_test_ds: OutputDataset,
    y_train_ds: OutputDataset,
    y_test_ds: OutputDataset
):

    import numpy as np
    from sklearn.model_selection import train_test_split

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)


    # Load dataset
    x = np.load(f"{dataset_path}/x.npy")
    y = np.load(f"{dataset_path}/y.npy")

    # Normalize pixel values
    x = x / 255.0

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=True, random_state=42
    )
            
    # Save data as artifacts
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")