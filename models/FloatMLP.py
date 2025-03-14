import torch.nn as nn
import torch


class FloatMLP(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        # get the parameters
        self.num_hidden_layers = kwargs.get("num_hidden_layers")

        # initialize the layers
        self.layers = nn.ModuleList()

        # first layer
        self.layers.append(
            nn.Linear(kwargs.get("in_features"), kwargs.get("hidden_size"))
        )
        self.layers.append(nn.ReLU())

        # hidden layers
        if self.num_hidden_layers >= int(1):
            for _ in range(self.num_hidden_layers - 1):
                self.layers.append(
                    nn.Linear(kwargs.get("hidden_size"), kwargs.get("hidden_size"))
                )
                self.layers.append(nn.ReLU())

        # output layer
        self.layers.append(
            nn.Linear(kwargs.get("hidden_size"), kwargs.get("out_features"))
        )

    def forward(self, inputs: torch.FloatTensor) -> torch.FloatTensor:
        for layer in self.layers:
            inputs = layer(inputs)
        return inputs
