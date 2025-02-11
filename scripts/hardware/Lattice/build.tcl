package require fileutil

if { $argc != 1 } {
    puts "The add.tcl script requires two numbers to be inputed."
    puts "must give one parameter, which is proj_dir"
} else {
    puts "This is a cutmized building script for Lattice Radiant"
    puts [lindex $argv 0]
    set proj_dir [lindex $argv 0]
}

# prj_create -name "radiant_project" -impl "impl_1" -dev iCE40UP5K-SG48I -performance "High-Performance_1.2V" -synthesis "synplify"
# prj_set_strategy_value -strategy Strategy1 {syn_pipelining_retiming=Pipelining and Retiming}

prj_create -name "radiant_project" -impl "impl_1" -dev iCE40UP5K-SG48I -performance "High-Performance_1.2V" -synthesis "lse"
prj_set_strategy_value -strategy Strategy1 lse_opt_goal=Timing lse_vhdl2008=True tmchk_enable_check=False

foreach file [fileutil::findByPattern "$proj_dir/source" "*.vhd"] { 
    prj_add_source $file
    }
# add constraints
prj_add_source $proj_dir/constraints/clock.sdc
prj_add_source "$proj_dir/constraints/pins.pdc"

# add set top module
prj_set_impl_opt -impl "impl_1" "top" "en_lattice_top" 

prj_run Synthesis -impl impl_1 -task SynTrace

prj_run Export -impl impl_1

prj_save
prj_close