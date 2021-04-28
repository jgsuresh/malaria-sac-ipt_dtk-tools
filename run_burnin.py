import numpy as np

from interventions import add_burnin_historical_interventions
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from reports import add_burnin_reports
from setup_sim import build_project_cb, set_ento_splines, burnin_setup


###################
# Run description #
###################
# Run burnins

##################################
# Core malaria config parameters #
##################################
from sweeps import modfn_sweep_over_habitat_scale

archetype = "Sahel"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files
# cb.set_param("Simulation_Duration", 1*365)
set_ento_splines(cb, habitat_scale=9.5, archetype=archetype)
burnin_setup(cb, archetype)

#################################################
# Campaign events that apply to ALL simulations #
#################################################
# add_standard_interventions(cb)
# add_burnin_historical_interventions(cb, archetype="Southern")

#####################
# Experiment sweeps #
#####################
modlists = []

# habitat_scale_array = np.round(np.linspace(8,9,11), decimals=1)
# habitat_scale_array = np.array([7.9,8.1,8.3,8.5,8.7,8.9])
# habitat_scale_array = np.array([7.5,7.6,7.7,7.8])
# habitat_scale_array = np.array([7.85,7.9,7.95,8])
habitat_scale_array = np.array([7.6,7.8,8.0,8.2,8.4,8.6,8.8,9.0,9.2,9.4])
modlist = modfn_sweep_over_habitat_scale(habitat_scale_array, archetype)
modlists.append(modlist)

num_seeds = 1
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)


####################
# Reports and logs #
####################
add_burnin_reports(cb, include_inset=True)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "sac_ipt_sahel_burnins_v2"
# comps_priority = "Normal"
comps_priority = "AboveNormal"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


