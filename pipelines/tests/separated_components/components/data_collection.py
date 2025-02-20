from kfp import dsl
from kfp.dsl import Dataset, Output

@dsl.component(
    base_image="registry.localhost/python_kfp:v3"
)
def data_collection(
    dataset: Output[Dataset]
):
    import os
    import numpy as np

    data = np.array(os.listdir('/mnt/datasets'))
    print(data)
    with open(dataset.path, 'wb') as f:
        np.save(f, data)