from typing import List
from kfp import dsl, compiler
from kfp.kubernetes import mount_pvc, add_node_selector


@dsl.component(
    base_image='python:3.12',
)
def mount_volume(pvc_name: str) -> List[str]:
    import os
    from time import sleep

    files = os.listdir('/mnt/datasets')
    print("=-" * 20)
    for i, file in enumerate(files):
        print(f"File {i}: {file}")
    print("=-" * 20)
    sleep(15)

    return files


@dsl.pipeline(
    name='Mount volume pipeline'
)
def mount_volume_pipeline(pvc_name: str) -> List[str]:
    task_instance = mount_volume(pvc_name=pvc_name)
    task_instance = add_node_selector(
        task=task_instance,
        label_key='kubernetes.io/hostname',
        label_value='k3s-node2'
    )
    task_instance = mount_pvc(
        task=task_instance,
        pvc_name=pvc_name,
        mount_path='/mnt/datasets'
    )

    return task_instance.output


compiler.Compiler().compile(mount_volume_pipeline, 'pipeline.yaml')