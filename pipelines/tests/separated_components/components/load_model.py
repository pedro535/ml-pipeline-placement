
from kfp import dsl
from kfp.dsl import Input, Model

@dsl.component(
    base_image="registry.localhost/python_kfp:v3"
)
def load_model(ml_model : Input[Model]):
    from tensorflow import keras
    import tensorflow as tf
    import os
    
    model = keras.models.load_model(ml_model.path + "/model.h5")
    print(model.summary())