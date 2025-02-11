# vivado -mode tcl -source power_estimation.tcl -tclargs reports  -nojournal -nolog
set saif_file_name [lindex $argv 0]
set report_dir [lindex $argv 1]
set sim_time [lindex $argv 2]
puts "$saif_file_name"
puts "$report_dir"

set proj_name "proj_power"

create_project -force $proj_name ./$proj_name

set_property part xc7s15ftgb196-2 [current_project]
add_files -scan_for_includes {./source}
update_compile_order -fileset sources_1
set_property default_lib work [current_project]

set_property library work [get_files -of [get_filesets {sources_1}]]
update_compile_order -fileset sources_1

after 5000 ;# waits for 5000 milliseconds

set_property top network [current_fileset]
update_compile_order -fileset sources_1

set_property top network_tb [get_filesets sim_1]
update_compile_order -fileset sim_1

add_files -fileset constrs_1 -norecurse {./constraints/power.xdc}

set_property -name {xsim.simulate.runtime} -value {$sim_time} -objects [get_filesets sim_1] 
set_property -name {xsim.simulate.log_all_signals} -value {true} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif_all_signals} -value {true} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif_scope} -value {uut} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif} -value "$saif_file_name" -objects [get_filesets sim_1]

reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

open_run synth_1 -name synth_1

launch_simulation -mode post-synthesis -type functional
close_sim

read_saif "$saif_file_name"

# report power consumption
report_power -file "$report_dir/power_report.txt"

# exit
