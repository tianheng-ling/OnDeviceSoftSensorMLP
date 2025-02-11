import re
from pathlib import Path
import pandas as pd
import os


def clean_key(key):
    return key.strip(" ...")[0]


def collect_design(design_dir: Path, data: dict):
    project_dir = design_dir / "radiant_temp"
    impl_dir = project_dir / "impl_1"
    if not impl_dir.exists():
        return

    par_report_path = impl_dir / "radiant_project_impl_1.par"
    if par_report_path.exists():
        with open(par_report_path, "rt") as f:
            par_report = f.read()

        for line in par_report.split("\n"):
            if m := re.match("\s+(\S*)\s+(\d+)/(\d+)\s+\d+% used", line):
                name, used, total = m.groups()
                used_relative = int(used) / int(total)
                data[name + "_used"] = int(used)
                data[name + "_used_relative"] = used_relative
    else:
        mrp_report_path = impl_dir / "radiant_project_impl_1.mrp"
        if mrp_report_path.exists():
            with open(mrp_report_path, "rt") as f:
                mrp_report = f.read()

            keywords = ["Number of LUT4s:", "Number of DSPs:", "Number of EBRs:"]

            for line in mrp_report.split("\n"):
                for keyword in keywords:
                    if keyword in line:
                        parts = line.split(":")
                        key = parts[0].strip()

                        used_value = int(parts[1].split("out of")[0].strip())
                        total_value = int(
                            parts[1].split("out of")[1].split("(")[0].strip()
                        )
                        used_relative = used_value / total_value

                        if key == "Number of LUT4s":
                            key = "LUT"
                        elif key == "Number of DSPs":
                            key = "DSP"
                        elif key == "Number of EBRs":
                            key = "EBR"

                        data[key + "_used"] = used_value
                        data[key + "_used_relative"] = used_relative

        else:
            srp_report_path = impl_dir / "radiant_project_impl_1_lattice.srp"
            if srp_report_path.exists():
                with open(srp_report_path, "rt") as f:
                    srp_report = f.read()

                keywords = [
                    "Device EBR Count ..............:",
                    "Used EBR Count ................:",
                    "Number of EBR Blocks Needed ...:",
                    "Device Register Count .........:",
                    "Number of registers needed ....:",
                    "Number of DSP Blocks:",
                ]

                tmp_results = {}
                tmp_results["LUT_used"] = 0
                tmp_results["LUT_total"] = 5280
                tmp_results["EBR_used"] = 0
                tmp_results["EBR_total"] = 20
                tmp_results["EBR_missing"] = 0
                tmp_results["DSP_used"] = 0

                for line in srp_report.split("\n"):
                    for keyword in keywords:
                        if keyword in line:
                            parts = line.split(":")
                            key = parts[0].strip()

                            if key == "Device EBR Count ..............":
                                key = "EBR_total"
                            elif key == "Used EBR Count ................":
                                key = "EBR_used"
                            elif key == "Number of EBR Blocks Needed ...":
                                key = "EBR_missing"
                            elif key == "Device Register Count .........":
                                key = "LUT_total"
                            elif key == "Number of registers needed ....":
                                key = "LUT_used"
                            elif key == "### Number of DSP Blocks":
                                key = "DSP_used"

                            value = int(parts[1].strip())
                            tmp_results[key] = value

                data["LUT_used"] = tmp_results["LUT_used"]
                data["LUT_used_relative"] = (
                    tmp_results["LUT_used"] / tmp_results["LUT_total"]
                )
                data["EBR_used"] = tmp_results["EBR_used"] + tmp_results["EBR_missing"]
                data["EBR_used_relative"] = (
                    tmp_results["EBR_used"] + tmp_results["EBR_missing"]
                ) / tmp_results["EBR_total"]
                data["DSP_used"] = tmp_results["DSP_used"]
                data["DSP_used_relative"] = tmp_results["DSP_used"] / 8

    return data


def analyze_power_total(path_list):

    df_list = []
    for path in path_list:
        if os.path.exists(path):
            parts = path.split("/")
            hidden_size = int(parts[2].split("_hs")[0])
            num_hidden_layers = int(parts[3].split("_hl")[0])
            quant_bits = int(parts[4].split("-bit")[0])
            fold_idx = int(parts[5].split("fold_")[1])
            timestamp = parts[6]

            data = {}
            data["num_hidden_layers"] = int(num_hidden_layers)
            data["hidden_size"] = int(hidden_size)
            data["quant_bits"] = int(quant_bits)
            data["fold_idx"] = int(fold_idx)
            data["timestamp"] = str(timestamp)

            with open(path, "rt") as f:
                power_report = f.read()

                match = re.search(
                    r"Total Power Est.\ Design  : (.+) W, (.+) W, (.+) W", power_report
                )
                static, dynamic, total = match.groups()
                data["static_power"] = float(static)
                data["dynamic_power"] = float(dynamic)
                data["total_power"] = float(total)

            df_list.append(pd.DataFrame([data]))
            # print("df_list", df_list)

        df = pd.concat(df_list, ignore_index=True)
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

    df.rename(columns={"Time taken for processing": "total_time_raw"}, inplace=True)

    df["total_time"] = df["total_time_raw"] / 10 * 62.5

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
    df_energy["total_energy"] = (
        df_energy["total_power"] * 1000 * df_energy["total_time"]
    )
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

    for i in ["total_time", "static_power", "dynamic_power", "total_power"]:
        df_energy[i] = df_energy[i] * 1000
        df_energy[i] = df_energy[i].round(2)
    df_energy["total_energy"] = df_energy["total_energy"].round(3)
    return df_energy
