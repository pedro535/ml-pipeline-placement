import os
from dotenv import load_dotenv
import argparse
import kfp

load_dotenv()
KFP_URL = os.getenv("KFP_URL")

parser = argparse.ArgumentParser()
parser.add_argument("--deploy", action="store_true", help="Deploy pipeline")
parser.add_argument("--stop", help="Stop pipeline execution")
args = parser.parse_args()


def deploy(client):
    client.create_run_from_pipeline_package(
        enable_caching=False,
        pipeline_file='pipeline.yaml',
        arguments={
            'pvc_name': 'datasets-pvc',
        },
    )


def stop(client, pipeline_id):
    client.terminate_run(pipeline_id)


if __name__ == "__main__":
    client = kfp.Client(host=KFP_URL)

    if args.deploy:
        deploy(client)
    elif args.stop:
        stop(client, args.stop)
    else:
        print("Please provide a valid argument")