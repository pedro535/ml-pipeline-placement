from typing import Dict, Any, List
from server.estimators import EstimatorInterface

# Source materials:
# - https://epoch.ai/blog/estimating-training-compute
# - https://epoch.ai/blog/backward-forward-FLOP-ratio
# - https://openai.com/index/ai-and-compute/


class CNN(EstimatorInterface):

    @staticmethod
    def _calculate_macs(layers: List[Dict[str, Any]]) -> int:
        macs = 0
        for layer in layers:
            input_shape = layer["input_shape"]
            output_shape = layer["output_shape"]
            layer_type = layer["type"]

            if layer_type == "Conv2D":    
                k_w, k_h = layer["kernel_size"]
                _, _, c_in = input_shape
                w_out, h_out, c_out = output_shape
                strides = layer["strides"][0]
                macs += (k_w * k_h * c_in * w_out * h_out * c_out) / strides**2
            elif layer_type == "MaxPooling2D":
                k_w, k_h = layer["pool_size"]
                _, _, c_in = input_shape
                w_out, h_out, c_out = output_shape
                macs += (k_w * k_h * c_in * w_out * h_out)
            elif layer_type == "Dense":
                n = input_shape[0]
                m = output_shape[0]
                macs += n * m + m
        return int(macs)


    @staticmethod
    def estimate_train(params: Dict[str, Any]) -> int:
        n_samples = params["n_samples"]
        n_epochs = params["n_epochs"]
        layers = params["layers"]

        macs = CNN._calculate_macs(layers)
        macs *= 3 * n_epochs * n_samples    # backward to forward ration is typically 2:1
        flops = 2 * macs                    # Assuming 2 flops per MAC
        return flops


    @staticmethod
    def estimate_pred(params: Dict[str, Any]) -> int:
        n_samples = params["n_samples"]
        layers = params["layers"]

        macs = CNN._calculate_macs(layers)
        macs *= n_samples                   # forward only
        flops = 2 * macs                    # Assuming 2 flops per MAC
        return flops