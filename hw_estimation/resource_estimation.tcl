# vivado -mode tcl -source resource_estimation.tcl -tclargs reports  -nojournal -nolog
# 
set report_dir [lindex $argv 0]

puts "$report_dir"

set proj_name "proj_resource"

create_project -force $proj_name ./$proj_name

set_property part xc7s15ftgb196-2 [current_project]
add_files -scan_for_includes {./source}
update_compile_order -fileset sources_1
set_property default_lib work [current_project]

set_property library work [get_files -of [get_filesets {sources_1}]]
update_compile_order -fileset sources_1

after 5000 ;# waits for 5000 milliseconds
set_property top env5_top_reconfig [current_fileset]
update_compile_order -fileset sources_1

add_files -fileset constrs_1 -norecurse {./constraints/env5_config.xdc}

# reset_run synth_1
# launch_runs impl_1 -jobs 8
# wait_on_run impl_1
# open_run impl_1 -name impl_1

reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

open_run synth_1 -name synth_1

report_utilization -file "$report_dir/utilization_report.txt"
report_utilization -hierarchical -file "$report_dir/utilization_breakdown.txt"
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -input_pins -routable_nets -name timing_1 -file "$report_dir/timing_report.txt"

# report power consumption
# report_power -file "$report_dir/power_report2.txt"
