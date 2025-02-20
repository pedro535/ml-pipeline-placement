from kfp import dsl
from kfp.dsl import Input, Dataset

@dsl.component(
    base_image="registry.localhost/python_kfp:v3"
)
def model_training(
    dataset: Input[Dataset]
):      
    import numpy as np

    data = np.load(dataset.path)
    print("Data received from previous task:")
    print(data)
    