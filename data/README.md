# Data Directory
This directory contains datasets and processing scripts used in our study.

## 📂 Directory Structure
data/
│── DS1.csv         # Public dataset (open-access)
│── EDA.ipynb       # Exploratory Data Analysis (EDA) notebook
│── data_process.py # Data preprocessing script
│── FlowDataset.py  # Custom dataset loader class

## 📄 Dataset Information

- **DS1.csv**:  
  A publicly available dataset from a system with a mud tank and Venturi structure. It includes **10 kHz** flow data from three level sensors, with Coriolis mass flowmeter readings as ground truth.  

- **Unavailable Datasets (DS2 & DS3)**:  
  These datasets, provided by **Viumdal et al.**, include **upward and downward flow trends** for enhanced evaluation but cannot be shared due to data ownership restrictions.  

## 🛠 Data Processing

- **EDA.ipynb**: Notebook for **exploratory data analysis (EDA)**, including statistics and visualizations.  
- **data_process.py**: Data preprocessing script (e.g., cleaning, normalization).  
- **FlowDataset.py**: Custom dataset loader module for training workflows.  

## 📖 Citation

If you use `DS1.csv` in your research or projects, please cite the original source:
```
  @inproceedings{noori2020non,
  title={Non-newtonian fluid flow measurement in open venturi channel using shallow neural network time series and non-contact level measurement radar sensors},
  author={Noori, NS and Waag, TI and Viumdal, H and Sharma, R and Jondahl, MH and Jinasena, A},
  booktitle={SPE Norway Subsurface Conference},
  pages={D011S001R003},
  year={2020},
  organization={SPE}
  }
```