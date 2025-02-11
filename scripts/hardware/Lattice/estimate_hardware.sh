#!/bin/bash
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=offscreen
export bindir=/home/tianhengling/lscc/radiant/2023.2/bin/lin64
source $bindir/radiant_env

txt_file_paths="scripts/hardware/selected_timestamps.txt"

build_tcl_path="scripts/hardware/ice40/build.tcl"
power_sim_path="scripts/hardware/ice40/power_sim.sh"
power_tcl_path="scripts/hardware/ice40/power_estimation.tcl"
power_sim_tcl_path="scripts/hardware/ice40/power_sim.tcl"
power_estimation_sh_path="scripts/hardware/ice40/power_estimation.sh"
source_dir="$(pwd)/experiments/quant"

while IFS= read -r line
do  
    (
    num_hidden_layers=$(echo $line | cut -d'/' -f3)
    hidden_size=$(echo $line | cut -d'/' -f4)
    quant_bits=$(echo $line | cut -d'/' -f5)
    fold_idx=$(echo $line | cut -d'/' -f6)
    timestamp=$(echo $line | cut -d'/' -f7)

    hw_dir="$source_dir/$num_hidden_layers/$hidden_size/$quant_bits/$fold_idx/$timestamp/hw/Lattice"
    vhdl_source_dir="$hw_dir/source"
    test_data_dir="$hw_dir/data"
    constrains_dir="$hw_dir/firmware/constraints"
    srcs_dir="$hw_dir/firmware/srcs"
    radiant_temp="$hw_dir/radiant_temp/"
    report_dir="$hw_dir/report"
    inference_time_dir="$hw_dir/inference_time"

    rm -rf $radiant_temp
    mkdir $radiant_temp
    cp -r $vhdl_source_dir "$radiant_temp/source"
    cp -r $constrains_dir "$radiant_temp/constraints"
    cp -r $test_data_dir "$radiant_temp/data"
    cp $build_tcl_path "$radiant_temp"
    cp $power_sim_path "$radiant_temp"
    cp $power_tcl_path "$radiant_temp"
    cp $power_sim_tcl_path "$radiant_temp"
    cp $power_estimation_sh_path "$radiant_temp"
    cp -r $srcs_dir/*.vhd "$radiant_temp/source"
    cp -r $srcs_dir/*/*.vhd "$radiant_temp/source"
    makefile_path="$hw_dir/makefile"
    cp $makefile_path "$radiant_temp"

    rm -rf $inference_time_dir
    mkdir $inference_time_dir
    cd $radiant_temp

    for dir in $(find $vhdl_source_dir -mindepth 1 -type d)
    do  
        module=$(basename $dir)
        if [[ $module == *"numerator"* ]] || [[ $module == *"denominator"* ]] || [[ $module == *"relu"* ]]; then
            continue
        fi
        make TESTBENCH=$module
        cp $radiant_temp/.simulation/make_output.txt $inference_time_dir/"ghdl_${module}_output.txt"
    done
    inference_time=$(grep "Time taken for processing" $inference_time_dir/"ghdl_network_output.txt" | awk -F'= ' '{print $2}' | awk '{print $1}')

    cd $radiant_temp
    pnmainc build.tcl $radiant_temp

    if [ -f "impl_1/radiant_project_impl_1_vo.vo" ]; then
        echo "radiant_project_impl_1_vo.vo exists, now do power estimation"
        sed -i "s/run 2989125 ns/run $inference_time fs /g" power_sim.tcl
        bash power_sim.sh 
        bash power_estimation.sh  
    else
        echo "radiant_project_impl_1_vo.vo does not exist, skip power estimation"
        exit 1
    fi
    )
done < "$txt_file_paths"
