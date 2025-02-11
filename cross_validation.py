import os
from pathlib import Path
from datetime import datetime
from torch.utils.data import DataLoader

from data.data_process import Normalizer, normalize_dataset
from models.set_model_params import set_model_params
from train_val import train_val
from test import test
from int_inference import int_inference


def cross_validation(cross_validation_config: dict):

    # unpack cross validation config
    data_config = cross_validation_config["data_config"]
    model_config = cross_validation_config["model_config"]
    exp_config = cross_validation_config["exp_config"]
    quant_config = cross_validation_config["quant_config"]

    all_fold_test_loss = []
    all_fold_test_loss_denorm = []

    for fold_idx, (train_dataset, val_dataset) in enumerate(
        data_config["train_val_dataset"]
    ):
        print(f"----------------------fold_{fold_idx}----------------------")

        # set experiment save directory
        base_exp_save_dir = exp_config["exp_save_dir"]
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fold_exp_save_dir = os.path.join(
            base_exp_save_dir, f"fold_{fold_idx}", current_timestamp
        )
        Path(fold_exp_save_dir).mkdir(parents=True, exist_ok=True)
        for sub_dir in ["", "figures", "logs"]:
            Path(os.path.join(fold_exp_save_dir, sub_dir)).mkdir(
                parents=True, exist_ok=True
            )
            exp_config.update(
                {   "exp_save_dir": fold_exp_save_dir,
                    "fig_save_dir": os.path.join(fold_exp_save_dir, "figures"),
                    "log_save_dir": os.path.join(fold_exp_save_dir, "logs"),
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
        dataset_normalized = normalize_dataset(
            data_config["dataset"], samples_normalizer, target_normalizer
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
        inference_dataloader = DataLoader(
            dataset_normalized, batch_size=1, shuffle=False
        )

        # set model params
        model_params = set_model_params(
            model_config=model_config,
            exp_config=exp_config,
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
        test_loss, test_loss_denorm = test(
            model_params=model_params,
            test_dataloader=test_dataloader,
            inference_dataloader=inference_dataloader,
            target_normalizer=target_normalizer,
            exp_config=exp_config,
        )

        all_fold_test_loss.append(test_loss.item())
        all_fold_test_loss_denorm.append(test_loss_denorm.item())

        # execute integer only inference
        if model_config["is_quantized"]:
            int_inference(
                test_dataloader=test_dataloader,
                inference_dataloader=inference_dataloader,
                target_normalizer=target_normalizer,
                model_params=model_params,
                exp_config=exp_config,
            )
        exp_config["exp_save_dir"] = base_exp_save_dir

    mean_fold_test_loss = sum(all_fold_test_loss) / len(all_fold_test_loss)
    mean_fold_test_loss_denorm = sum(all_fold_test_loss_denorm) / len(
        all_fold_test_loss_denorm
    )

    print(f"Mean of test loss: {mean_fold_test_loss}")
    print(f"Mean of test loss denorm: {mean_fold_test_loss_denorm}")

    return mean_fold_test_loss, mean_fold_test_loss_denorm
