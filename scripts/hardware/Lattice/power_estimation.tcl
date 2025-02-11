# this script estimates power consumption of a design, baed on a file called 
# `power_simulation.vcd`, the report will be called as `power_estimation_report.txt`
# this file should be copied and executed in `$radiant_temp` folder

prj_open "radiant_project.rdf"

if {![file exists "power_estimation.pcf"]} {
    pwc_new_project "power_estimation.pcf" -udb "impl_1/radiant_project_impl_1.udb"
    pwc_save_project "power_estimation.pcf"

    prj_add_source "power_estimation.pcf"
    prj_save
} else {
    pwc_open_project "power_estimation.pcf"
}

pwc_set_afpervcd -vcd "power_simulation/power_simulation.vcd" -module i_top caseinsensitive

pwc_calculate
pwc_gen_report "power_estimation_report.txt"

pwc_save_project "power_estimation.pcf"
pwc_close_project
prj_close