import os
from pathlib import Path
from datetime import datetime
from torch.utils.data import DataLoader

from data.data_process import Normalizer, normalize_dataset
from models.set_model_params import set_model_params
from train_val import train_val
from test import test
from utils.set_paths import set_base_paths
from hw_converter.convert2hw import convert2hw


def cross_validation(cross_validation_config: dict):

    # unpack cross validation config
    data_config = cross_validation_config["data_config"]
    model_config = cross_validation_config["model_config"]
    exp_config = cross_validation_config["exp_config"]
    quant_config = cross_validation_config["quant_config"]
    convert2hw_config = cross_validation_config["convert2hw_config"]

    all_fold_test_loss = []
    all_fold_test_loss_denorm = []

    for fold_idx, (train_dataset, val_dataset) in enumerate(
        data_config["train_val_dataset"]
    ):
        print(f"----------------------fold_{fold_idx}----------------------")

        # set experiment save directory
        fold_exp_save_dir, fold_fig_save_dir, fold_log_save_dir = set_base_paths(
            Path(exp_config["exp_base_save_dir"]) / f"fold_{fold_idx}"
        )
        exp_config.update(
            {
                "exp_save_dir": fold_exp_save_dir,
                "fig_save_dir": fold_fig_save_dir,
                "log_save_dir": fold_log_save_dir,
            }
        )

        # normalize data
        samples_normalizer = Normalizer.from_data(train_dataset[:][0])
        target_normalizer = Normalizer.from_data(train_dataset[:][1])
        train_dataset_normalized = normalize_dataset(
            train_dataset, samples_normalizer, target_normalizer
        )
        val_dataset_normalized = normalize_dataset(
            val_dataset, samples_normalizer, target_normalizer
        )
        test_dataset_normalized = normalize_dataset(
            data_config["test_dataset"], samples_normalizer, target_normalizer
        )

        # prepare dataloader
        train_dataloader = DataLoader(
            train_dataset_normalized, batch_size=exp_config["batch_size"], shuffle=True
        )
        val_dataloader = DataLoader(
            val_dataset_normalized, batch_size=exp_config["batch_size"], shuffle=False
        )
        test_dataloader = DataLoader(
            test_dataset_normalized, batch_size=1, shuffle=False
        )

        # set model params
        model_params = set_model_params(
            model_config=model_config,
            quant_config=quant_config,
        )

        # train and validate
        train_val(
            model_params=model_params,
            train_dataloader=train_dataloader,
            val_dataloader=val_dataloader,
            target_normalizer=target_normalizer,
            exp_config=exp_config,
        )

        # test
        test_config = {
            "model_params": model_params,
            "test_dataloader": test_dataloader,
            "target_normalizer": target_normalizer,
            "exp_config": exp_config,
        }
        test_loss, test_loss_denorm = test(**test_config)

        all_fold_test_loss.append(test_loss.item())
        all_fold_test_loss_denorm.append(test_loss_denorm.item())

        # execute integer only inference
        if model_config["is_qat"]:
            model_params["do_int_forward"] = True
            test(**test_config)

            # convert to hardware
            for target_hw in ["amd", "lattice"]:
                convert2hw(
                    test_dataset=test_dataset_normalized,
                    subset_size=convert2hw_config["subset_size"],
                    model_params=model_params,
                    exp_save_dir=exp_config["exp_save_dir"],
                    target_hw=target_hw,
                )

        exp_config["exp_save_dir"] = exp_config["exp_base_save_dir"]

    mean_fold_test_loss = sum(all_fold_test_loss) / len(all_fold_test_loss)
    mean_fold_test_loss_denorm = sum(all_fold_test_loss_denorm) / len(
        all_fold_test_loss_denorm
    )

    print(f"Mean of test loss: {mean_fold_test_loss}")
    print(f"Mean of test loss denorm: {mean_fold_test_loss_denorm}")

    return mean_fold_test_loss, mean_fold_test_loss_denorm
