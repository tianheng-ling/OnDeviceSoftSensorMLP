import torch
import torch.nn as nn
from pathlib import Path

from elasticai.creator.nn.integer.linear import Linear
from elasticai.creator.nn.integer.relu import ReLU
from elasticai.creator.nn.integer.sequential import Sequential


class QuantMLP(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        # get the parameters
        self.num_hidden_layers = kwargs.get("num_hidden_layers")
        self.do_int_forward = kwargs.get("do_int_forward")
        self.name = kwargs.get("name")

        # initialize the self.layers
        self.layers = nn.ModuleList()

        # input layer
        self.layers.append(
            Linear(
                name="linear_0",
                in_features=kwargs.get("input_size"),
                out_features=kwargs.get("hidden_size"),
                bias=True,
                quant_bits=kwargs.get("input_linear_quant_bits"),
                device=kwargs.get("device")
            )
        )
        self.layers.append(
            ReLU(name="relu_0", 
            quant_bits=kwargs.get("input_relu_quant_bits"),
            device=kwargs.get("device"),)
        )

        # hidden self.layers
        if self.num_hidden_layers >= int(1):
            for i in range(self.num_hidden_layers):
                self.layers.append(
                    Linear(
                        name=f"linear_{i+1}",
                        in_features=kwargs.get("hidden_size"),
                        out_features=kwargs.get("hidden_size"),
                        bias=True,
                        quant_bits=kwargs.get(f"hidden_linear_{i}_quant_bits"),
                        device=kwargs.get("device")
                    )
                )
                self.layers.append(
                    ReLU(
                        name=f"relu_{i+1}",
                        quant_bits=kwargs.get(f"hidden_linear_{i}_relu_quant_bits"),
                        device=kwargs.get("device")
                    )
                )

        # output layer
        self.layers.append(
            Linear(
                name=f"linear_{self.num_hidden_layers+1}",
                in_features=kwargs.get("hidden_size"),
                out_features=kwargs.get("output_size"),
                bias=True,
                quant_bits=kwargs.get("output_linear_quant_bits"),
                device=kwargs.get("device")
            )
        )

        self.sequential = Sequential(*self.layers, name=self.name,quant_data_file_dir=kwargs.get("quant_data_file_dir"))

    def forward(
        self,
        inputs: torch.FloatTensor,
    ) -> torch.FloatTensor:

        if self.do_int_forward:
            self.sequential.precompute()
            inputs = inputs.to("cpu")
            q_inputs = self.sequential.quantize_inputs(inputs)
            q_outputs = self.sequential.int_forward(q_inputs)
            return self.sequential.dequantize_outputs(q_outputs)
        else:
            return self.sequential.forward(inputs)
