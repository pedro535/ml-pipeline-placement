from mlopx import Component, Pipeline

from component_1 import component_1
from component_2 import component_2


c1 = Component(
    image="registry.localhost/python_kfp:v3",
    func=component_1,
    args={
        "message": "Hello world"
    }
)

c2 = Component(
    image="registry.localhost/python_kfp:v3",
    func=component_2,
    args={
        "message": "Ola mundo"
    }
)

pipeline = Pipeline(name="simple_pipeline")
pipeline.add([c1, c2])
pipeline.submit("http://127.0.0.1:8000")