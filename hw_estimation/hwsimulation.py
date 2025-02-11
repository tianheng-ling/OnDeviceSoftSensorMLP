import os
import shutil

from default_config import model_default_config
from elasticai.creator.file_generation.on_disk_path import OnDiskPath
from elasticai.creator.nn.integer.vhdl_test_automation.create_makefile import (
    create_makefile,
)
from elasticai.creator.vhdl.system_integrations.firmware_env5 import (
    FirmwareENv5,
)


def hwsimulation(exp_save_dir, design, target_hw):

    # get makefile
    destination_dir = os.path.join(exp_save_dir, f"hw/{target_hw}")
    custom_stop_time = "500000000ns"
    create_makefile(destination_dir, custom_stop_time)

    quant_data_dir = os.path.join(exp_save_dir, "hw/data")

    # fpga-specific files
    if target_hw == "AMD":
        firmware = FirmwareENv5(
            design,
            x_num_values=model_default_config["input_size"],
            y_num_values=model_default_config["output_size"],
            id=66,
        )
        firmware.save_to(OnDiskPath(name="firmware", parent=str(destination_dir)))
        shutil.copytree(quant_data_dir, os.path.join(destination_dir, "data"))
        shutil.copy(
            "hw_converter/AMD/firmware/constraints/power.xdc",
            os.path.join(destination_dir, "firmware/constraints"),
        )

    elif target_hw == "Lattice":
        source_firmware_dir = os.path.join("hw_converter/Lattice", "firmware")
        shutil.copytree(source_firmware_dir, os.path.join(destination_dir, "firmware"))
        shutil.copytree(quant_data_dir, os.path.join(destination_dir, "data"))

        source_ram_path = "hw_converter/ram/dual_port_2_clock_ram.vhd"
        dest_ram_path = (
            str(destination_dir) + "/source/network/dual_port_2_clock_ram.vhd"
        )
        shutil.copy(source_ram_path, dest_ram_path)
    else:
        raise ValueError(f"Invalid target_hw: {target_hw}")
