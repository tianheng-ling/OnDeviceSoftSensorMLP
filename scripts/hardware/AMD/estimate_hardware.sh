#!/bin/bash
txt_file_paths="scripts/hardware/selected_timestamps.txt"
resource_timing_estimation_path="scripts/hardware/xs15/resource_timing_estimation.tcl"
power_estimation_path="scripts/hardware/xs15/power_estimation.tcl"
source_dir="$(pwd)/experiments/quant"

while IFS= read -r line
do  
    (
    num_hidden_layers=$(echo $line | cut -d'/' -f3)
    hidden_size=$(echo $line | cut -d'/' -f4)
    quant_bits=$(echo $line | cut -d'/' -f5)
    fold_idx=$(echo $line | cut -d'/' -f6)
    timestamp=$(echo $line | cut -d'/' -f7)

    model_dir="$source_dir/$num_hidden_layers/$hidden_size/$quant_bits/$fold_idx/$timestamp/hw/AMD"
    vhdl_source_dir="$model_dir/source"
    test_data_dir="$model_dir/data"
    constrains_dir="$model_dir/firmware/constraints"
    makefile_name="$model_dir/makefile"
    srcs_dir="$model_dir/firmware/srcs"

    vivado_temp="$model_dir/temp_vivado"
    report_dir="$model_dir/report"
    inference_time_dir="$model_dir/inference_time"

    rm -rf $vivado_temp
    mkdir $vivado_temp
    cp $resource_timing_estimation_path "$vivado_temp"
    cp $power_estimation_path "$vivado_temp"
    cp -r $vhdl_source_dir "$vivado_temp" 
    cp -r $test_data_dir "$vivado_temp"
    cp -r $constrains_dir "$vivado_temp"
    cp $makefile_name "$vivado_temp"
    
    cp -r $srcs_dir/*.vhd "$vivado_temp/source"
    cp -r $srcs_dir/*/*.vhd "$vivado_temp/source"
    
    rm -rf $inference_time_dir
    mkdir $inference_time_dir
    cd $vivado_temp
    for dir in $(find $vhdl_source_dir -mindepth 1 -type d)
    do  
        module=$(basename $dir)
        if [[ $module == *"numerator"* ]] || [[ $module == *"denominator"* ]] || [[ $module == *"relu"* ]]; then
            continue
        fi
        make TESTBENCH=$module
        cp $vivado_temp/.simulation/make_output.txt $inference_time_dir/"ghdl_${module}_output.txt"
    done
    inference_time=$(grep "Time taken for processing" $inference_time_dir/"ghdl_network_output.txt" | awk -F'= ' '{print $2}' | awk '{print $1}')

    absolute_data_dir="${vivado_temp}/data"
    sed -i "s|./data|$absolute_data_dir|g" ./source/network/network_tb.vhd
    saif_file_name="${vivado_temp}/sim_wave.saif"

    rm -rf $report_dir
    mkdir $report_dir
    source /tools/Xilinx/Vivado/2019.2/settings64.sh
    vivado -mode tcl -source resource_timing_estimation.tcl -tclargs $report_dir  -nojournal -nolog < /dev/null
    vivado -mode tcl -source power_estimation.tcl -tclargs $saif_file_name $report_dir "${inference_time}fs" -nojournal -nolog < /dev/null

    remove vivado_temp
    rm -rf $vivado_temp
    )
done < "$txt_file_paths"