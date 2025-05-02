from kfp import dsl, Client
from kfp.kubernetes import mount_pvc, add_node_selector, add_toleration
from kfp_data_preprocessing import data_preprocessing
from kfp_model_training import model_training
from kfp_model_evaluation import model_evaluation


@dsl.pipeline(name="cifar10_cnn")
def cifar10_cnn():
    data_preprocessing_task = data_preprocessing(dataset_path="/mnt/datasets/CIFAR_10")
    model_training_task = model_training(
        x_train_ds=data_preprocessing_task.outputs["x_train_ds"],
        y_train_ds=data_preprocessing_task.outputs["y_train_ds"],
    )
    model_evaluation_task = model_evaluation(
        model_artifact=model_training_task.outputs["model_artifact"],
        x_test_ds=data_preprocessing_task.outputs["x_test_ds"],
        y_test_ds=data_preprocessing_task.outputs["y_test_ds"],
    )
    data_preprocessing_task = mount_pvc(
        task=data_preprocessing_task,
        pvc_name="datasets-pvc",
        mount_path="/mnt/datasets",
    )

    data_preprocessing_task = data_preprocessing_task.set_memory_request("2881088Ki")
    model_training_task = model_training_task.set_memory_request("2881088Ki")
    model_evaluation_task = model_evaluation_task.set_memory_request("576216Ki")


client = Client(host="http://kfp.local")
run = client.create_run_from_pipeline_func(
    pipeline_func=cifar10_cnn, enable_caching=False
)
print("Run ID: ", run.run_id)
