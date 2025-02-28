import os
from dotenv import load_dotenv
import kfp

load_dotenv()
KFP_URL = os.getenv("KFP_URL")


if __name__ == "__main__":
    client = kfp.Client(host=KFP_URL)

    client.create_run_from_pipeline_package(
        enable_caching = False,
        pipeline_file = "pipeline.yaml",
        arguments = {
            "dataset_path": "/mnt/datasets/german_traffic_signs",
            "epochs": 2,
            "batch_size": 128
        },
    )