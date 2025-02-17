import kfp

client = kfp.Client(host="http://localhost:3000")

run = client.create_run_from_pipeline_package(
    pipeline_file='pipeline.yaml',
    namespace='tests',
    arguments={
        'recipient': 'World',
    },
)
