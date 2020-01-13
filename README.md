Description of Files:

1. activate_interfaces.sh: Script to activate the eth1 and eth2 interfaces on the newly migrated VNF
2. collect_metrics.sh: Script to execute the parsing scripts depending on the action performed and return the output
3. merit.py: Same as before - just added 'predict_homing_cost' to generate a random number in order to test the different actions

Pending items:
1. Calculation of BW (currently it's just KBin)
2. Possibly generate different training files for each action as header will be different
