import numpy as np

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_simple_hs, \
    add_bednets_for_population_and_births, archetype_seasonal_usage, set_school_children_ips_TEST
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from malaria.reports.MalariaReport import add_summary_report
from reports import add_burnin_reports, add_scenario_reports, add_testing_reports, summary_age_bins
from setup_sim import build_project_cb, set_ento_splines, burnin_setup

###################
# Run description #
###################
# Run sweep of term timing for a given archetype/school calendar

##################################
# Core malaria config parameters #
##################################
from sweeps import modfn_sweep_over_habitat_scale, modfn_sweep_over_scenarios, modfn_sweep_over_timings


archetype = "Central"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files
num_years = 2
cb.set_param("Simulation_Duration", num_years*365)

# sim id: f16b8c35-7192-eb11-a2ce-c4346bcb1550
cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\sac_ipt_central_burnins_additional_20210430_153643\\158\\ac9\\c4c\\158ac9c4-c9a9-eb11-a2e3-c4346bcb7275\\output")
cb.set_param("Serialized_Population_Filenames", ["state-18250.dtk"])


#################################################
# Campaign events that apply to ALL simulations #
#################################################
set_school_children_ips(cb)
# set_school_children_ips_TEST(cb)
add_simple_hs(cb, 0.7)
add_bednets_for_population_and_births(cb,
                                      0.7,
                                      seasonal_dependence=archetype_seasonal_usage[archetype],
                                      discard_config_type="default")


#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 3
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_timings(archetype, num_years=num_years)
modlists.append(modlist)

####################
# Reports and logs #
####################
# add_scenario_reports(cb, include_inset=False)
# add_testing_reports(cb)
add_summary_report(cb, start=365)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "central_sac_ipt_timing_sweep"
# comps_priority = "BelowNormal"
comps_priority = "AboveNormal"
# comps_priority = "AboveNormal"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


