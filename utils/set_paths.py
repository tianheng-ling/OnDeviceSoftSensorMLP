import os
from pathlib import Path
from datetime import datetime


def set_base_paths(exp_base_save_dir: str):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    exp_save_dir = Path(exp_base_save_dir) / timestamp

    fig_save_dir, log_save_dir = exp_save_dir / "figs", exp_save_dir / "logs"

    for path in [exp_save_dir, fig_save_dir, log_save_dir]:
        os.makedirs(path, exist_ok=True)

    return exp_save_dir, fig_save_dir, log_save_dir
