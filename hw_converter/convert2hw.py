import os
import torch

from default_config import DEVICE
from models.build_model import build_model
from elasticai.creator.file_generation.on_disk_path import OnDiskPath


def convert2hw(model_params: dict, exp_save_dir: str, target_hw: str) -> OnDiskPath:

    # initialize model
    model = build_model(**model_params).to(DEVICE)

    # load model
    model_path = os.path.join(exp_save_dir, "best_model.pth")
    model.load_state_dict(torch.load(model_path, weights_only=True))

    # translate model for fpga
    destination = OnDiskPath(name=f"hw/{target_hw}/source", parent=str(exp_save_dir))
    model.eval()
    model.sequential.precompute()
    design = model.sequential.create_design("network")
    design.save_to(destination)

    return design
