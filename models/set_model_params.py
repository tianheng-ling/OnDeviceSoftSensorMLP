from default_config import DEVICE


def set_model_params(model_config: dict, quant_config: dict = None):
    is_qat = model_config["is_qat"]
    model_params = {
        "in_features": model_config["in_features"],
        "hidden_size": model_config["hidden_size"],
        "out_features": model_config["out_features"],
        "num_hidden_layers": model_config["num_hidden_layers"],
        "is_qat": is_qat,
    }
    if is_qat:
        model_params["name"] = "network"
        model_params["quant_bits"] = quant_config["quant_bits"]
        model_params["do_int_forward"] = False
        model_params["device"] = DEVICE
    return model_params
