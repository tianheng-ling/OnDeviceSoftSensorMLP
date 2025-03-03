import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

data_default_config = {
    "data_file_dir": "data/DS1.csv",
    "test_size": 0.15,
    "random_state": 0,
    "num_kfold": 7,
}

model_default_config = {
    "in_features": 3,
    "out_features": 1,
}

exp_default_config = {
    "num_epochs": 100,
    "patience_epochs": 10,
    "batch_size": 100,
    "lr": 0.001,
}

quant_default_config = {
    "quant_bits": None,
}
