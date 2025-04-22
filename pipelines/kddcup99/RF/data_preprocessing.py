from mlopx.pipelines.artifacts import OutputDataset


def data_preprocessing(
    dataset_path: str,
    x_train_ds: OutputDataset,
    x_test_ds: OutputDataset,
    y_train_ds: OutputDataset,
    y_test_ds: OutputDataset
):

    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder

    def npy_save(data, path):
        with open(path, "wb") as f:
            np.save(f, data)


    # Load dataset
    col_names = ["duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent", "hot", 
                "num_failed_logins", "logged_in", "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations", 
                "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count", "srv_count", 
                "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
                "srv_diff_host_rate", "dst_host_count","dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate", 
                "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate", 
                "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label"]
    
    df = pd.read_csv(dataset_path, header=None, names=col_names)

    # Encode categorical variables
    categorical_features = ["protocol_type", "service", "flag"]
    for feature in categorical_features:
        le = LabelEncoder()
        df[feature] = le.fit_transform(df[feature])

    # Encode target variable (attack label): Binary classification (normal vs attack)
    df['label'] = df['label'].apply(lambda x: 0 if x == 'normal.' else 1)

    # Split features and target
    x = df.drop("label", axis=1)
    y = df["label"]

    # Split into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=True, random_state=42
    )

    # Scale the features
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    # Save data as artifacts
    npy_save(x_train, x_train_ds.path)
    npy_save(y_train, y_train_ds.path)
    npy_save(x_test, x_test_ds.path)
    npy_save(y_test, y_test_ds.path)
    print("Data saved as artifacts")