# OnDeviceSoftSensorMLP

## Overview
OnDeviceSoftSensorMLP is an open-source repository that demonstrates the end-to-end development and deployment of Multi-Layer Perceptron (MLP)-based soft sensors on embedded FPGA platforms. This repository is designed to support diverse deployment objectives, such as high precision, low latency, low power consumption, and energy efficiency.

## Status
The code is being finalized and will be released soon. Please stay tuned for updates.


## Features
- **Quantization-Aware Training (QAT)**: Train integer-only quantized models tailored for deployment on resource-constrained FPGAs.
- **FPGA-Compatible Accelerator Generation**: Automatically generate FPGA accelerators using VHDL templates with the support of the ElasticAI.Creator Toolchain.
- **Hardware Simulation and Validation**: Simulate, synthesize, and deploy accelerators to validate performance, including inference latency, power, and precision.
- **Support for Diverse FPGA Platforms**: Includes workflows tailored for the AMD Spartan-7 XC7S15 and the Lattice iCE40UP5K.

## Use Case
This repository was developed as part of a case study on fluid flow estimation using soft sensors. It demonstrates how to:
- Develop adaptable MLP-based soft sensors.
- Deploy models on FPGA platforms to meet specific precision, latency, and energy efficiency goals.

## Supported FPGA Platforms
- AMD Spartan-7 XC7S15
- Lattice iCE40UP5K

## Integration with ElasticAI.Creator

The workflow in this repository is designed to work seamlessly with [ElasticAI.Creator](https://github.com/es-ude/elastic-ai.creator), our custom open-source toolchain for:
- Quantization-aware training of integer-only models.
- Generating FPGA-compatible accelerators from trained models.

## Roadmap
1. Finalize the workflow and scripts for model quantization, accelerator generation, and validation.
2. Provide a comprehensive set of tutorials for deploying soft sensors.
3. Expand support to include other sequential neural network architectures.

## How to Cite
If you find this repository helpful, please cite our accompanying research paper:
TODO

## License

This repository is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or feedback, please feel free to open an issue or contact us at tianheng.ling@uni-due.de.
