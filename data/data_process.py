import torch
import numpy as np
from dataclasses import dataclass
from sklearn.model_selection import KFold
from torch.utils.data import Dataset, Subset, TensorDataset, random_split


def split_indices(num_samples: int, test_size: float, random_state: int):

    np.random.seed(random_state)
    indices = np.random.permutation(num_samples)
    split = int(np.floor(test_size * num_samples))
    train_indices, test_indices = indices[split:], indices[:split]

    return train_indices, test_indices


def kfold_split_dataset(dataset: Dataset, k: int, test_size: float, random_state: int):
    num_samples = len(dataset)
    train_indices, test_indices = split_indices(num_samples, test_size, random_state)

    train_val_dataset = Subset(dataset, train_indices)
    test_dataset = Subset(dataset, test_indices)

    kf = KFold(n_splits=k, shuffle=True, random_state=random_state)
    train_val_indices = train_val_dataset.indices

    folds = []
    for train_indices, val_indices in kf.split(train_val_indices):
        train_dataset = Subset(train_val_dataset, train_indices)
        val_dataset = Subset(train_val_dataset, val_indices)
        folds.append((train_dataset, val_dataset))

    return folds, test_dataset


def split_dataset(
    dataset: Dataset, val_size: float, test_size: float, random_state: int
):
    len_dataset = len(dataset)
    test_size = int(test_size * len_dataset)
    val_size = int(val_size * len_dataset)
    train_size = len_dataset - val_size - test_size

    train_dataset, val_dataset, test_dataset = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(random_state),
    )

    return train_dataset, val_dataset, test_dataset


@dataclass(frozen=True)
class Normalizer:
    minimum: float
    maximum: float

    @staticmethod
    def from_data(data: torch.Tensor) -> "Normalizer":
        return Normalizer(minimum=float(data.min()), maximum=float(data.max()))

    def normalize(self, data: torch.Tensor) -> torch.Tensor:
        return (data - self.minimum) / (self.maximum - self.minimum)

    def rescale(self, data: torch.Tensor) -> torch.Tensor:
        return data * (self.maximum - self.minimum) + self.minimum


def normalize_dataset(
    data: Dataset, samples_normalizer: Normalizer, target_normalizer: Normalizer
) -> TensorDataset:

    samples, labels = data[:]
    return TensorDataset(
        samples_normalizer.normalize(samples), target_normalizer.normalize(labels)
    )
