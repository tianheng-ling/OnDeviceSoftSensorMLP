import re
import os
import pandas as pd
from pathlib import Path


def clean_key(key):
    return key.strip("| ").replace(" ", "_")


def analyze_resource_total(path_list):
    df_list = []
    keywords = ["| Slice LUTs", "|   LUT as Memory", "| Block RAM Tile", "| DSPs"]

    for path in path_list:

        hidden_size = path.split("/")[2]
        num_hidden_layers = path.split("/")[3]
        quant_bits = path.split("/")[4]
        fold_idx = path.split("/")[5]
        timestamp = path.split("/")[6]

        path = os.path.join(path + "/report", "utilization_report.txt")
        if Path(path).exists():
            with open(path, "r") as f:
                lines = f.readlines()
        else:
            continue

        tmp_results = {}
        for line in lines:
            for keyword in keywords:
                if keyword in line:

                    parts = line.split("|")
                    used_value = (
                        float(parts[2].strip()) if parts[2].strip() != "" else 0
                    )
                    total_value = (
                        float(parts[4].strip()) if parts[4].strip() != "" else 0
                    )
                    utils_value = (
                        float(parts[5].strip()) if parts[5].strip() != "" else 0
                    )
                    clean_keyword = clean_key(keyword)

                    tmp_results[clean_keyword + "_used"] = used_value
                    tmp_results[clean_keyword + "_total"] = total_value
                    tmp_results[clean_keyword + "_used_util"] = utils_value

        tmp_results.update(
            {
                "num_hidden_layers": num_hidden_layers,
                "hidden_size": hidden_size,
                "quant_bits": quant_bits,
                "fold_idx": fold_idx,
                "timestamp": timestamp,
            }
        )

        df_list.append(pd.DataFrame([tmp_results]))

    df = pd.concat(df_list, ignore_index=True)

    df["quant_bits"] = df["quant_bits"].apply(lambda x: re.sub(r"\D", "", x))
    df["quant_bits"] = df["quant_bits"].astype(int)
    df["fold_idx"] = df["fold_idx"].apply(lambda x: re.sub(r"\D", "", x))
    df["fold_idx"] = df["fold_idx"].astype(int)
    df["timestamp"] = df["timestamp"].astype(str)
    df["hidden_size"] = df["hidden_size"].apply(lambda x: re.sub(r"\D", "", x))
    df["hidden_size"] = df["hidden_size"].astype(int)
    df["num_hidden_layers"] = df["num_hidden_layers"].apply(
        lambda x: re.sub(r"\D", "", x)
    )
    df["num_of_layers"] = df["num_hidden_layers"].astype(int) + 4

    for col in df.columns:
        if "Slice_LUTs_" in col:
            df.rename(columns={col: col.replace("Slice_LUTs_", "luts_")}, inplace=True)
        elif "LUT_as_Memory_" in col:
            df.rename(
                columns={col: col.replace("LUT_as_Memory_", "luts_mem_")}, inplace=True
            )
        elif "Block_RAM_Tile_" in col:
            df.rename(
                columns={col: col.replace("Block_RAM_Tile_", "brams_")}, inplace=True
            )
        elif "DSPs_" in col:
            df.rename(columns={col: col.replace("DSPs_", "dsps_")}, inplace=True)
        else:
            pass

    new_order = [
        "timestamp",
        "fold_idx",
        "num_of_layers",
        "hidden_size",
        "quant_bits",
        "luts_used",
        "luts_total",
        "luts_used_util",
        "brams_used",
        "brams_total",
        "brams_used_util",
        "dsps_used",
        "dsps_total",
        "dsps_used_util",
    ]
    df = df.reindex(columns=new_order)

    return df


def analyze_power_total(path_list):
    df_list = []
    keywords = ["Total On-Chip Power (W)", "Dynamic (W)", "Device Static (W)"]

    for path in path_list:
        if os.path.exists(path):
            parts = path.split("/")

            hidden_size = int(parts[2].split("_hs")[0])
            num_hidden_layers = int(parts[3].split("_hl")[0])
            quant_bits = int(parts[4].split("-bit")[0])
            fold_idx = int(parts[5].split("fold_")[1])
            timestamp = parts[6]

            with open(path, "r") as f:
                lines = f.readlines()

            tmp_results = {}
            for line in lines:

                for keyword in keywords:
                    if keyword in line:
                        parts = line.split("|")
                        value = float(parts[2].strip())
                        clean_keyword = clean_key(keyword)
                        tmp_results[clean_keyword] = value

            tmp_results.update(
                {
                    "num_hidden_layers": num_hidden_layers,
                    "hidden_size": hidden_size,
                    "quant_bits": quant_bits,
                    "fold_idx": fold_idx,
                    "timestamp": timestamp,
                }
            )

            df_list.append(pd.DataFrame([tmp_results]))
        else:
            print(f"File not found: {path}")

        df = pd.concat(df_list, ignore_index=True)

        df["num_hidden_layers"] = df["num_hidden_layers"].astype(int)
        df["quant_bits"] = df["quant_bits"].astype(int)
        df["hidden_size"] = df["hidden_size"].astype(int)
        df["timestamp"] = df["timestamp"].astype(str)
        df["fold_idx"] = df["fold_idx"].astype(int)

        # rename the column of Total_On-Chip_Power_(W) as total_power
        df.rename(columns={"Total_On-Chip_Power_(W)": "total_power"}, inplace=True)
        df.rename(columns={"Dynamic_(W)": "dynamic_power"}, inplace=True)
        df.rename(columns={"Device_Static_(W)": "static_power"}, inplace=True)

        df["total_power"] = df["total_power"] * 1000
        df["dynamic_power"] = df["dynamic_power"] * 1000
        df["static_power"] = df["static_power"] * 1000

        new_order = [
            "timestamp",
            "fold_idx",
            "num_hidden_layers",
            "hidden_size",
            "quant_bits",
            "static_power",
            "dynamic_power",
            "total_power",
        ]
        df = df.reindex(columns=new_order)

    return df


def analyze_timing(path_list):
    df_list = []
    keywords = ["Time taken for processing"]

    for path in path_list:

        if os.path.exists(path):

            parts = path.split("/")
            hidden_size = int(parts[2].split("_hs")[0])
            num_hidden_layers = int(parts[3].split("_hl")[0])
            quant_bits = int(parts[4].split("-bit")[0])
            fold_idx = int(parts[5].split("fold_")[1])
            timestamp = parts[6]

            with open(path, "r") as f:
                lines = f.readlines()

            tmp_results = {}
            for line in lines:
                for keyword in keywords:
                    if keyword in line:
                        parts = line.split("=")
                        value = float(parts[1].strip().split(" ")[0])
                        value = value / 1000000000000
                        tmp_results[keyword] = value

            tmp_results.update(
                {
                    "num_hidden_layers": num_hidden_layers,
                    "hidden_size": hidden_size,
                    "quant_bits": quant_bits,
                    "fold_idx": fold_idx,
                    "timestamp": timestamp,
                }
            )

            df_list.append(pd.DataFrame([tmp_results]))

    df = pd.concat(df_list, ignore_index=True)

    df["num_hidden_layers"] = df["num_hidden_layers"].astype(int)
    df["quant_bits"] = df["quant_bits"].astype(int)
    df["hidden_size"] = df["hidden_size"].astype(int)
    df["timestamp"] = df["timestamp"].astype(str)
    df["fold_idx"] = df["fold_idx"].astype(int)

    df.rename(columns={"Time taken for processing": "total_time"}, inplace=True)
    new_order = [
        "timestamp",
        "fold_idx",
        "num_hidden_layers",
        "hidden_size",
        "quant_bits",
        "total_time",
    ]
    df = df.reindex(columns=new_order)

    return df


def calculate_energy_total(df_power, df_timing):
    df_energy = pd.merge(
        df_power,
        df_timing,
        on=[
            "timestamp",
            "fold_idx",
            "num_hidden_layers",
            "hidden_size",
            "quant_bits",
        ],
    )
    df_energy["total_energy"] = df_energy["total_power"] * df_energy["total_time"]
    new_order = [
        "timestamp",
        "fold_idx",
        "num_hidden_layers",
        "hidden_size",
        "quant_bits",
        "total_time",
        "static_power",
        "dynamic_power",
        "total_power",
        "total_energy",
    ]
    df_energy = df_energy.reindex(columns=new_order)

    df_energy["total_energy"] = df_energy["total_energy"].round(3)
    df_energy["total_time"] = df_energy["total_time"] * 1000
    df_energy["total_time"] = df_energy["total_time"].round(2)
    return df_energy
