import torch
import pandas as pd
from pathlib import Path
from torch.utils.data import Dataset


class FlowDataset(Dataset):
    def __init__(self, data_path: str | Path) -> None:
        super().__init__()
        data = pd.read_csv(data_path)
        self.X = torch.tensor(data.iloc[:, :-1].values, dtype=torch.float32)
        self.y = torch.tensor(data.iloc[:, -1].values, dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, index) -> tuple[torch.Tensor, torch.Tensor]:
        return self.X[index], self.y[index]
