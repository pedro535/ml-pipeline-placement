from typing import List, Dict
import keras
import json


class ModelDetails:

    @staticmethod
    def tf_dnn_layers(model: keras.Model, display: bool = False) -> List[Dict]:
        """
        Return layer details of a TensorFlow DNN model.
        """
        layers = []
        for layer in model.layers:
            details = {
                "type": layer.__class__.__name__,
                "input_shape": layer.input.shape[1:],
                "output_shape": layer.output.shape[1:],
                "params": layer.count_params()
            }

            if isinstance(layer, keras.layers.Conv2D):
                details["kernel_size"] = layer.kernel_size
                details["strides"] = layer.strides
            elif isinstance(layer, keras.layers.MaxPooling2D):
                details["pool_size"] = layer.pool_size

            layers.append(details)
        
        if display:
            print(json.dumps(details, indent=4))

        return layers
