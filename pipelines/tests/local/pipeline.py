from kfp import dsl, compiler, local
from typing import List
from kfp.dsl import InputPath

local.init(runner=local.DockerRunner())

@dsl.component
def list_files(input_path: InputPath(str)) -> List[str]:
    import os
    files = os.listdir(input_path)
    print(files)
    return files

@dsl.pipeline(
    name='List files pipeline',
)
def my_pipeline(input_path: str) -> List[str]:
    list_files_task = list_files(input_path=input_path)
    return list_files_task.output

pipeline_task = my_pipeline(input_path='/mnt')