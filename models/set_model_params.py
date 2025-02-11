from pathlib import Path
from default_config import DEVICE


def set_model_params(model_config: dict, exp_config: dict, quant_config: dict = None):

    input_size = model_config["input_size"]
    hidden_size = model_config["hidden_size"]
    output_size = model_config["output_size"]
    num_hidden_layers = model_config["num_hidden_layers"]
    is_quantized = model_config["is_quantized"]
    exp_save_dir = exp_config["exp_save_dir"]

    model_params = {
        "name": "network",
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "num_hidden_layers": num_hidden_layers,
        "is_quantized": is_quantized,
    }

    if is_quantized:
        quant_bits = quant_config["quant_bits"]

        quant_data_file_dir = Path(exp_save_dir) / "hw" / "data"
        Path(quant_data_file_dir).mkdir(parents=True, exist_ok=True)
        model_params["quant_data_file_dir"] = quant_data_file_dir
        model_params["do_int_forward"] = False
        model_params["device"] = DEVICE

        # input layer
        model_params["input_linear_quant_bits"] = quant_bits
        model_params["input_relu_quant_bits"] = quant_bits

        # hidden layers
        if num_hidden_layers >= int(1):
            for i in range(num_hidden_layers):
                model_params[f"hidden_linear_{i}_quant_bits"] = quant_bits
                model_params[f"hidden_linear_{i}_relu_quant_bits"] = quant_bits

        # output layer
        model_params["output_linear_quant_bits"] = quant_bits

    return model_params
