import os
import torch
import logging
import numpy as np
from pathlib import Path
from torch.utils.data import DataLoader
from sklearn.metrics import r2_score

from default_config import DEVICE
from models.build_model import build_model
from utils.plots import save_pred_truth_line_plot


def test(
    model_params: dict,
    test_dataloader: DataLoader,
    inference_dataloader: DataLoader,
    target_normalizer: object,
    exp_config: dict,
) -> object:

    # initialize model
    model = build_model(**model_params).to(DEVICE)

    # load model
    model_path = os.path.join(exp_config["exp_save_dir"], "best_model.pth")
    model.load_state_dict(torch.load(model_path, weights_only=True))

    # set up logging
    logging_path = Path(exp_config["log_save_dir"]) / "test_logfile.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",
        handlers=[logging.FileHandler(logging_path), logging.StreamHandler()],
    )

    # perform test
    model.to(DEVICE)
    model.eval()
    all_test_preds = []
    all_test_targets = []
    all_test_preds_denorm = []
    all_test_targets_denorm = []

    with torch.no_grad():
        for test_samples, test_target in test_dataloader:

            test_samples = test_samples.to(DEVICE)
            test_target = test_target.to(DEVICE)

            test_pred = model(inputs=test_samples)

            all_test_preds.append(test_pred.flatten().cpu().numpy())
            all_test_targets.append(test_target.flatten().cpu().numpy())

    all_test_preds = torch.tensor(np.array(all_test_preds))
    all_test_targets = torch.tensor(np.array(all_test_targets))
    all_test_preds_denorm = target_normalizer.rescale(all_test_preds)
    all_test_targets_denorm = target_normalizer.rescale(all_test_targets)

    # calculate MSE
    test_loss = torch.nn.MSELoss()(all_test_preds, all_test_targets)
    test_loss_denorm = torch.nn.MSELoss()(
        all_test_preds_denorm, all_test_targets_denorm
    )

    # calculate MAPE
    test_mape = (
        torch.mean(torch.abs((all_test_preds - all_test_targets) / all_test_targets))
        * 100
    )
    test_mape_denorm = (
        torch.mean(
            torch.abs(
                (all_test_preds_denorm - all_test_targets_denorm)
                / all_test_targets_denorm
            )
        )
        * 100
    )

    # calculate R2
    test_r2 = r2_score(all_test_targets, all_test_preds)
    test_r2_denorm = r2_score(all_test_targets_denorm, all_test_preds_denorm)

    prefix = (
        "int_test"
        if hasattr(model, "do_int_forward") and model.do_int_forward == True
        else "test"
    )
    print(f"---------------- {prefix} ----------------")
    logging.info(f"{prefix}_loss: {test_loss:.4f}")
    logging.info(f"{prefix}_loss_denorm: {test_loss_denorm:.4f}")
    logging.info(f"{prefix}_mape: {test_mape:.4f}")
    logging.info(f"{prefix}_mape_denorm: {test_mape_denorm:.4f}")
    logging.info(f"{prefix}_r2: {test_r2:.4f}")
    logging.info(f"{prefix}_r2_denorm: {test_r2_denorm:.4f}")

    # perform inference on the whole dataset (just for visualization)
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for inference_samples, inference_target in inference_dataloader:

            inference_samples = inference_samples.to(DEVICE)
            inference_target = inference_target.to(DEVICE)

            pred = model(inputs=inference_samples)

            all_preds.append(pred.flatten().cpu().numpy())
            all_targets.append(inference_target.flatten().cpu().numpy())

    all_preds = torch.tensor(np.array(all_preds))
    all_targets = torch.tensor(np.array(all_targets))

    all_preds_denorm = target_normalizer.rescale(all_preds)
    all_targets_denorm = target_normalizer.rescale(all_targets)

    prefix = (
        "int_inference"
        if hasattr(model, "do_int_forward") and model.do_int_forward
        else "inference"
    )
    save_pred_truth_line_plot(
        pred=all_preds_denorm,
        truth=all_targets_denorm,
        fig_save_dir=exp_config["fig_save_dir"],
        prefix=prefix,
    )

    return test_loss, test_loss_denorm
