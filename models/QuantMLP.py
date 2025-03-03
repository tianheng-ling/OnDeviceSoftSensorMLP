import torch
import torch.nn as nn

from elasticai.creator.nn.integer.linear import Linear
from elasticai.creator.nn.integer.relu import ReLU
from elasticai.creator.nn.integer.sequential import Sequential
from elasticai.creator.nn.integer.vhdl_test_automation.file_save_utils import (
    save_quant_data,
)


class QuantMLP(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        in_features = kwargs.get("in_features")
        hidden_size = kwargs.get("hidden_size")
        out_features = kwargs.get("out_features")
        self.num_hidden_layers = kwargs.get("num_hidden_layers")

        self.name = kwargs.get("name")
        self.quant_bits = kwargs.get("quant_bits")
        self.do_int_forward = kwargs.get("do_int_forward")
        self.quant_data_dir = kwargs.get("quant_data_dir", None)
        device = kwargs.get("device")

        # initialize the self.layers
        self.layers = nn.ModuleList()

        # input layer
        self.layers.append(
            Linear(
                name="linear_0",
                in_features=in_features,
                out_features=hidden_size,
                bias=True,
                quant_bits=self.quant_bits,
                quant_data_dir=self.quant_data_dir,
                device=device,
            )
        )
        self.layers.append(
            ReLU(
                name="relu_0",
                quant_bits=self.quant_bits,
                quant_data_dir=self.quant_data_dir,
                device=device,
            )
        )

        # hidden self.layers
        if self.num_hidden_layers >= int(1):
            for i in range(self.num_hidden_layers):
                self.layers.append(
                    Linear(
                        name=f"linear_{i+1}",
                        in_features=hidden_size,
                        out_features=hidden_size,
                        bias=True,
                        quant_bits=self.quant_bits,
                        quant_data_dir=self.quant_data_dir,
                        device=device,
                    )
                )
                self.layers.append(
                    ReLU(
                        name=f"relu_{i+1}",
                        quant_bits=self.quant_bits,
                        quant_data_dir=self.quant_data_dir,
                        device=device,
                    )
                )

        # output layer
        self.layers.append(
            Linear(
                name=f"linear_{self.num_hidden_layers+1}",
                in_features=hidden_size,
                out_features=out_features,
                bias=True,
                quant_bits=self.quant_bits,
                quant_data_dir=self.quant_data_dir,
                device=device,
            )
        )

        self.sequential = Sequential(
            *self.layers,
            name=self.name,
            quant_data_dir=self.quant_data_dir,
        )

    def forward(
        self,
        inputs: torch.FloatTensor,
    ) -> torch.FloatTensor:

        if self.do_int_forward:
            self.sequential.precompute()
            inputs = inputs.to("cpu")
            q_inputs = self.sequential.quantize_inputs(inputs)
            save_quant_data(q_inputs, self.quant_data_dir, f"{self.name}_q_x")
            q_outputs = self.sequential.int_forward(q_inputs)
            save_quant_data(q_outputs, self.quant_data_dir, f"{self.name}_q_y")
            return self.sequential.dequantize_outputs(q_outputs)
        else:
            return self.sequential.forward(inputs)
