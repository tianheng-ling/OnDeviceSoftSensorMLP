import torch
import logging
import numpy as np
from pathlib import Path
from torch.utils.data import DataLoader

from default_config import DEVICE
from utils.EarlyStopping import EarlyStopping
from models.build_model import build_model
from utils.plots import plot_learning_curve


def train_val(
    model_params: dict,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    target_normalizer: object,
    exp_config: dict,
) -> object:

    # initialize model
    model = build_model(**model_params).to(DEVICE)

    # set up logging
    logging_path = Path(exp_config["log_save_dir"]) / "train_val_logfile.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",
        handlers=[logging.FileHandler(logging_path), logging.StreamHandler()],
    )

    # set up training
    optimizer = torch.optim.Adam(
        model.parameters(), lr=exp_config["lr"], betas=(0.9, 0.98), eps=1e-9
    )

    criterion = torch.nn.MSELoss()
    early_stopping = EarlyStopping(
        patience=exp_config["patience_epochs"],
        verbose=True,
        delta=0,
        path=exp_config["exp_save_dir"],
        trace_func=print,
    )

    # execute train and validation phase
    all_train_epoch_losses = []
    all_train_epoch_losses_denorm = []
    all_val_epoch_losses = []
    all_val_epoch_losses_denorm = []

    for epoch in range(exp_config["num_epochs"]):

        # train loop
        model.train()
        sum_train_batch_losses = 0
        sum_train_batch_losses_denorm = 0
        for train_samples, train_target in train_dataloader:

            train_samples = train_samples.to(DEVICE)
            train_target = train_target.to(DEVICE)

            train_pred = model(inputs=train_samples)
            train_pred_denorm = target_normalizer.rescale(train_pred)
            train_target_denorm = target_normalizer.rescale(train_target)

            train_batch_loss = criterion(train_pred.flatten(), train_target)
            train_batch_loss_denorm = criterion(
                train_pred_denorm.flatten(), train_target_denorm
            )

            optimizer.zero_grad()
            train_batch_loss.backward()
            optimizer.step()

            sum_train_batch_losses += train_batch_loss.item()
            sum_train_batch_losses_denorm += train_batch_loss_denorm.item()

        train_epoch_loss = sum_train_batch_losses / len(train_dataloader)
        train_epoch_loss_denorm = sum_train_batch_losses_denorm / len(train_dataloader)

        all_train_epoch_losses.append(train_epoch_loss)
        all_train_epoch_losses_denorm.append(train_epoch_loss_denorm)

        # validation loop
        model.eval()
        sum_val_batch_losses = 0
        sum_val_batch_losses_denorm = 0
        with torch.no_grad():
            for val_samples, val_target in val_dataloader:

                val_samples = val_samples.to(DEVICE)
                val_target = val_target.to(DEVICE)

                val_pred = model(inputs=val_samples)
                val_pred_denorm = target_normalizer.rescale(val_pred)
                val_target_denorm = target_normalizer.rescale(val_target)

                val_batch_loss = criterion(val_pred.flatten(), val_target)
                val_batch_loss_denorm = criterion(
                    val_pred_denorm.flatten(), val_target_denorm
                )

                sum_val_batch_losses += val_batch_loss.item()
                sum_val_batch_losses_denorm += val_batch_loss_denorm.item()

            val_epoch_loss = sum_val_batch_losses / len(val_dataloader)
            val_epoch_loss_denorm = sum_val_batch_losses_denorm / len(val_dataloader)

            all_val_epoch_losses.append(val_epoch_loss)
            all_val_epoch_losses_denorm.append(val_epoch_loss_denorm)

        # early stopping
        early_stopping(val_epoch_loss, model)
        if early_stopping.early_stop:
            logging.info("executed_valid_epochs: {}".format(epoch - 10))
            break

        logging.info(f'[Epoch {epoch}/{exp_config["num_epochs"]}]')
        logging.info(
            f"Train: Loss: {train_epoch_loss:.4f}; Loss Denorm: {train_epoch_loss_denorm:.4f}"
        )
        logging.info(
            f"Validation: Loss: {val_epoch_loss:.4f}; Loss Denorm: {val_epoch_loss_denorm:.4f}"
        )

    exp_train_loss = np.min(all_train_epoch_losses)
    exp_train_loss_denorm = np.min(all_train_epoch_losses_denorm)
    exp_val_loss = np.min(all_val_epoch_losses)
    exp_val_loss_denorm = np.min(all_val_epoch_losses_denorm)

    print(f"Train Loss: {exp_train_loss}; Train Loss Denorm: {exp_train_loss_denorm}")
    print(
        f"Validation Loss: {exp_val_loss}; Validation Loss Denorm: {exp_val_loss_denorm}"
    )

    plot_learning_curve(
        epochs=range(1, len(all_train_epoch_losses) + 1),
        train_losses=all_train_epoch_losses,
        val_losses=all_val_epoch_losses,
        save_path=exp_config["fig_save_dir"],
        type="loss",
    )

    return model
