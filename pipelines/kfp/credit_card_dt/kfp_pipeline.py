from kfp import dsl, Client
from kfp.kubernetes import mount_pvc, add_node_selector, add_toleration
from kfp_data_preprocessing import data_preprocessing
from kfp_model_training import model_training
from kfp_model_evaluation import model_evaluation


@dsl.pipeline(name="credit_card_dt")
def credit_card_dt():
    data_preprocessing_task = data_preprocessing(
        dataset_path="/mnt/datasets/credit_card/credit_card.csv"
    )
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

    # data_preprocessing_task = data_preprocessing_task.set_memory_request("11718Ki")
    # model_training_task = model_training_task.set_memory_request("9000Ki")
    # model_evaluation_task = model_evaluation_task.set_memory_request("2250Ki")


client = Client(host="http://kfp.local")
run = client.create_run_from_pipeline_func(
    pipeline_func=credit_card_dt, enable_caching=False
)
print("Run ID: ", run.run_id)
