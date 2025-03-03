import os
import argparse

from default_config import (
    DEVICE,
    data_default_config,
    model_default_config,
    exp_default_config,
    quant_default_config,
)
from data.FlowDataset import FlowDataset
from data.data_process import kfold_split_dataset
from cross_validation import cross_validation


def main(args) -> None:

    # set data configs
    data_config = data_default_config.copy()
    dataset = FlowDataset(data_config["data_file_dir"])
    train_val_dataset, test_dataset = kfold_split_dataset(
        dataset,
        k=data_config["num_kfold"],
        test_size=data_config["test_size"],
        random_state=data_config["random_state"],
    )
    data_config.update(
        {
            "dataset": dataset,
            "train_val_dataset": train_val_dataset,
            "test_dataset": test_dataset,
        }
    )

    # set model configs
    model_config = model_default_config.copy()
    model_config.update(
        {
            "hidden_size": args.hidden_size,
            "num_hidden_layers": args.num_hidden_layers,
            "is_qat": args.is_qat,
        }
    )

    # set convert2hw configs
    convert2hw_config = {
        "subset_size": args.subset_size,
    }

    # set quantization configs
    quant_config = quant_default_config.copy()
    if args.is_qat:
        quant_config.update({"quant_bits": args.quant_bits})

    # set experiment configs
    exp_config = exp_default_config.copy()
    exp_config.update(
        {
            "exp_base_save_dir": args.exp_base_save_dir,
            "device": DEVICE,
        }
    )
    # set cross validation config and run
    cross_validation_config = {
        "data_config": data_config,
        "model_config": model_config,
        "exp_config": exp_config,
        "quant_config": quant_config,
        "convert2hw_config": convert2hw_config,
    }
    cross_validation(cross_validation_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # model parameters
    parser.add_argument(
        "--is_qat",
        action="store_true",
        help="to distinguish float and quantized model",
    )
    parser.add_argument("--hidden_size", type=int)
    parser.add_argument("--num_hidden_layers", type=int)

    # experiment parameters
    parser.add_argument("--exp_base_save_dir", type=str)

    # quantization parameters
    parser.add_argument("--quant_bits", type=int, choices=[8, 6, 4])

    # hw simulation config
    parser.add_argument(
        "--subset_size",
        type=int,
        help="Number of samples to use for HW simulation",
    )

    args = parser.parse_args()
    main(args)
