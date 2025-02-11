import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42


def plot_raw_data(df: pd.DataFrame):
    colors = [
        (47 / 255, 173 / 255, 78 / 255),
        (17 / 255, 111 / 255, 178 / 255),
        (245 / 255, 143 / 255, 56 / 255),
        (202 / 255, 14 / 255, 16 / 255),
    ]
    figsize = (4, 6)
    ylabel_list = ["Level (mm)", "Level (mm)", "Level (mm)", "Flow (kg/min)"]
    ylims_list = [(20, 120), (20, 120), (20, 120), (200, 650)]

    axes = df.plot(subplots=True, figsize=figsize, color=colors, xlabel="Index")
    for ax, ylabel, ylim in zip(axes, ylabel_list, ylims_list):
        ax.set_ylabel(ylabel)
        ax.set_ylim(ylim)
        ax.legend(loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_learning_curve(
    epochs: list[int],
    train_losses: list[float],
    val_losses: list[float],
    save_path: str,
    type: str,
):
    save_path = os.path.join(save_path, f"learning_curve.png")
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(epochs, train_losses, label=f"Train {type}")
    ax.plot(epochs, val_losses, label=f"Validation {type}")
    ax.set_xlabel("Epochs")
    ax.set_ylabel(f"{type}")
    ax.legend()
    plt.tight_layout()
    fig.savefig(save_path)


def save_resisual_plot(
    pred: np.ndarray, truth: np.ndarray, fig_save_dir: str, prefix: str
):
    fig_save_path = os.path.join(fig_save_dir, f"{prefix}_residual_plot.png")
    residuals = (abs(pred - truth) / truth) * 100

    plt.figure(figsize=(6, 4))
    plt.scatter(pred, residuals)
    plt.xlabel("Predicted Values")
    plt.ylabel("Residuals(%) between Predicted and Ground Truth Values")
    plt.axhline(y=0, color="r", linestyle="--")
    plt.savefig(fig_save_path)
    plt.close()


def save_pred_truth_line_plot(
    pred: np.ndarray, truth: np.ndarray, fig_save_dir: str, prefix: str
):

    fig_path = os.path.join(fig_save_dir, f"{prefix}_pred_truth.png")

    plt.figure(figsize=(6, 4))
    plt.plot(range(len(pred)), pred, label="Predictions")
    plt.plot(range(len(truth)), truth, label="Ground Truth")
    plt.legend()
    plt.savefig(fig_path)
    plt.close()
