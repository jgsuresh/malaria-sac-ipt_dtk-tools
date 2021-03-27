import numpy as np

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_simple_hs, \
    add_bednets_for_population_and_births, archetype_seasonal_usage, set_school_children_ips_TEST
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from reports import add_burnin_reports, add_scenario_reports, add_testing_reports
from setup_sim import build_project_cb, set_ento_splines, burnin_setup, scenario_setup

###################
# Run description #
###################
# Run sweep of term timing for a given archetype/school calendar

##################################
# Core malaria config parameters #
##################################
from sweeps import modfn_sweep_over_habitat_scale, modfn_sweep_over_scenarios, modfn_sweep_over_timings

cb = build_project_cb()


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files
archetype = "Southern"
cb.set_param("Simulation_Duration", 1*365)
# sim id: 54e57670-bb8c-eb11-a2ce-c4346bcb1550
# cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\southern_burnin_sweep_20210324_161122\\73e\\576\\70b\\73e57670-bb8c-eb11-a2ce-c4346bcb1550\\output")

# sim id: 53e57670-bb8c-eb11-a2ce-c4346bcb1550
# cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\southern_burnin_sweep_20210324_161122\\74e\\576\\70b\\74e57670-bb8c-eb11-a2ce-c4346bcb1550\\output")

# sim id: 951c23d8-e88c-eb11-a2ce-c4346bcb1550
cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\southern_burnin_v3_20210324_213625\\68d\\51b\\e7e\\68d51be7-e88c-eb11-a2ce-c4346bcb1550\\output")
cb.set_param("Serialized_Population_Filenames", ["state-18250.dtk"])

#fixme sweep over timings, get analyzer which extracts average pfpr for final year, and create a csv of the results

#################################################
# Campaign events that apply to ALL simulations #
#################################################
set_school_children_ips(cb)
# set_school_children_ips_TEST(cb)
add_simple_hs(cb, 0.7)
add_bednets_for_population_and_births(cb,
                                      0.7,
                                      seasonal_dependence=archetype_seasonal_usage["Southern"],
                                      discard_config_type="default")


#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 3
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_timings(archetype)
modlists.append(modlist)

####################
# Reports and logs #
####################
add_scenario_reports(cb, include_inset=False)
# add_testing_reports(cb)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "southern_sac_ipt_timing_sweep_baseline"
# comps_priority = "BelowNormal"
comps_priority = "Normal"
# comps_priority = "AboveNormal"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


