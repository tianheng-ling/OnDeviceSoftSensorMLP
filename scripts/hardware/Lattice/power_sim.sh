# This script starts a VHDL simulation with a software call modelsim
# to log the switching activities of each logic circuit for one/several
# inferences
# the switching activity information is critical for accurate dynamic power estimation.

# this file should be copied and executed in `$radiant_temp` folder

# Change the path if you are not using the thread station
RADIANT="/home/tianhengling/lscc/radiant/2023.2" 

rm -rf power_sim
LM_LICENSE_FILE="$RADIANT/license/license.dat" "$RADIANT/modeltech/linuxloem/vsim"  -c -do power_sim.tcl