import numpy as np

from interventions import add_burnin_historical_interventions
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from reports import add_burnin_reports, add_scenario_reports
from setup_sim import build_project_cb, set_ento_splines, burnin_setup

###################
# Run description #
###################
# Run scenarios that draw from burnins

##################################
# Core malaria config parameters #
##################################
from sweeps import modfn_sweep_over_habitat_scale, modfn_sweep_over_scenarios, modfn_sweep_over_burnins

archetype = "Southern"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files

cb.set_param("Simulation_Duration", 2*365)

#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 10
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_burnins(archetype)
modlists.append(modlist)

modlist = modfn_sweep_over_scenarios(archetype) #, specific_scenarios_to_run=[0,3,34]
modlists.append(modlist)


####################
# Reports and logs #
####################
add_scenario_reports(cb, include_inset=True, include_bednet_events_in_counter=True)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "southern_sac_ipt_scenarios"
comps_priority = "Normal"
# comps_priority = "Highest"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


