# OnDeviceSoftSensorMLP

This is the code for our paper titled **Configurable Multi-Layer Perceptron-Based Soft Sensors on Embedded Field Programmable Gate Arrays: Targeting Diverse Deployment Goals in Fluid Flow Estimation**


This study presents a comprehensive workflow for developing and deploying Multi-Layer Perceptron (MLP)-based soft sensors on embedded FPGAs, addressing diverse deployment objectives. The proposed workflow extends our prior research by introducing greater model adaptability. It supports various configurations—spanning layer counts, neuron counts, and quantization bitwidths—to accommodate the constraints and capabilities of different FPGA platforms. The workflow incorporates a custom-developed, open-source toolchain ElasticAI.Creator that facilitates quantization-aware training, integer-only inference, automated accelerator generation using VHDL templates, and synthesis alongside performance estimation. A case study on fluid flow estimation was conducted on two FPGA platforms: the AMD Spartan-7 XC7S15 and the Lattice iCE40UP5K. For precision-focused and latency-sensitive deployments, a six-layer, 60-neuron MLP accelerator quantized to 8 bits on the XC7S15 achieved an MSE of 56.56, an MAPE of 1.61%, and an inference latency of 23.87 μs. Moreover, for low-power and energy-constrained deployments, a five-layer, 30-neuron MLP accelerator quantized to 8 bits on the iCE40UP5K achieved an inference latency of 83.37 μs, a power consumption of 2.06 mW, and an energy consumption of just 0.172 μJ per inference. These results confirm the workflow’s ability to identify optimal FPGA accelerators tailored to specific deployment requirements, achieving a balanced trade-off between precision, inference latency, and energy efficiency.

If you find this repository useful, please consider citing our [paper](https://www.mdpi.com/1424-8220/25/1/83):
```
@article{ling2024configurable,
title={Configurable Multi-Layer Perceptron-Based Soft Sensors on Embedded Field Programmable Gate Arrays: Targeting Diverse Deployment Goals in Fluid Flow Estimation},
author={Ling, Tianheng and Qian, Chao and Klann, Theodor Mario and Hoever, Julian and Einhaus, Lukas and Schiele, Gregor},
journal={Sensors (Basel, Switzerland)},
volume={25},
number={1},
pages={83},
year={2024}
}
```

## 🚀 Overview

OnDeviceSoftSensorMLP is an open-source repository demonstrating the **end-to-end development and deployment** of Multi-Layer Perceptron (MLP)-based soft sensors on **embedded FPGA platforms**. It enables **quantized MLP models** to run efficiently on resource-constrained hardware, balancing **precision, latency, power and energy consumption**.

## ✨ Features

✔ **Quantization-Aware Training (QAT)** – Train **integer-only** quantized models for low-power deployment on FPGAs.  
✔ **FPGA Accelerator Generation** – Automate the creation of hardware accelerators using **VHDL templates** via [ElasticAI.Creator](https://github.com/es-ude/elastic-ai.creator).  
✔ **Hardware Simulation & Deployment** – Simulate, synthesize, and deploy models, validating inference time, power and enery consumption. 

## 🖥 Supported FPGA Platforms
- **AMD Spartan-7 XC7S15**
- **Lattice iCE40UP5K**

## 🛠 Integration with ElasticAI.Creator
This repository is designed to work with **[ElasticAI.Creator](https://github.com/es-ude/elastic-ai.creator)**, our open-source toolchain that:
- **Performs Quantization-Aware Training (QAT)** for integer-only inference.
- **Generates FPGA-compatible accelerators** from trained models.

## 📦 Installation
To set up your environment, follow these steps:

#### 1️⃣ Clone the Repository
```bash
git clone git@github.com:Edwina1030/OnDeviceSoftSensorMLP.git
cd OnDeviceSoftSensorMLP
```
#### 2️⃣ Create and Activate a Virtual Environment
Using Python’s built-in venv (recommended)
```
python -m venv venv --python=python3.11     # Create virtual environment
source venv/bin/activate                    # On macOS/Linux
venv\Scripts\activate                       # On Windows
```
#### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
#### 4️⃣ Verify Installation
```
python -c "import torch; print(torch.__version__)"
```
Ensure that dependencies are correctly installed and compatible with your system.

## ⚙️ FPGA Setup

This project involves AMD Spartan-7 XC7S15 and Lattice iCE40UP5K platforms. Follow the instructions below to set up the FPGA toolchains accordingly.

#### 1️⃣ Install AMD Vivado (for Spartan-7)

Vivado is the official development environment for AMD (Xilinx) FPGAs, supporting FPGA design, synthesis, and deployment.
**Installation Steps**
1. Download AMD Vivado (recommended version: 2022.2 or later).
2. Choose the WebPACK edition (free version), which supports Spartan-7.
3. During installation, select the FPGA design suite and ensure Spartan-7-related components are included.
4. After installation, add Vivado to your environment variables:
```
source /opt/Xilinx/Vivado/2022.2/settings64.sh  # Linux
C:\Xilinx\Vivado\2022.2\settings64.bat          # Windows
```

#### 2️⃣ Install Lattice Radiant (for iCE40UP5K)

Lattice Radiant is the official development environment for Lattice FPGAs, supporting low-power FPGA design.
**Installation Steps**
1. Download Lattice Radiant (recommended version: 2023.1 or later).
2. Register and obtain a free license.
3. During installation, ensure that the iCE40UP5K components are selected.
4. Add Radiant to your environment variables:
```
source /usr/local/lscc/radiant/2023.1/settings.sh  # Linux
set PATH=C:\lscc\radiant\2023.1\bin\nt64;%PATH%  # Windows
```

## 🧪 Experiment
### 1️⃣ Train the FP32 Models as Baseline
```
bash scripts/software/float/train.sh
```
### 2️⃣ Train the Quantized Models
```
bash scripts/software/quant/train.sh
```
### 3️⃣ Select Records for Hardware Simulation
copy path to ``scripts/hardware/selected_timestamps.txt``

### 4️⃣ Execute Hardware Simulation
```
bash scripts/hardware/AMD/estimate_hardware.sh      # For AMD FPGA
bash scripts/hardware/Lattice/estimate_hardware.sh  # For Lattice FPGA
```
### 5️⃣ Evaluation Hardware Performance
Use the analysis scripts in the ``utils`` folder for extract information from reports
- analyze_amd_report.py      
- analyze_lattice_report.py 


### Related Repositories
This project is part of a broader family of FPGA-optimized time-series models. You may also be interested in:

- **On Device Swipe Direction Recognition with 1D(Sep)CNNs** → [GitHub Repository](https://github.com/tianheng-ling/Smatable)
- **On Device Transformers across various time-series analysis tasks** → [GitHub Repository](https://github.com/tianheng-ling/TinyTransformer4TS) 
- **On Device Sewage Overflow Forefasting with Transforemrs and LSTMs** → [GitHub Repository](https://github.com/tianheng-ling/EdgeOverflowForecast)
- **On Device Running Gait Recognition with various time-series models** → [GitHub Repository](https://github.com/tianheng-ling/StrikeWatch)


## 🎓 Acknowledgement
Funding for this study was provided by the Federal Ministry for Economic Affairs and Climate Action of Germany to the RIWWER project (01MD22007C).

## Contact
For questions or feedback, please feel free to open an issue or contact us at ling.tianheng@gmail.com.