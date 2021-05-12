import numpy as np
from dtk.interventions.ivermectin import add_ivermectin

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_scenario_specific_itns, \
    add_scenario_specific_healthseeking, add_scenario_specific_ipt, set_school_children_ips_for_complex_age_dist, \
    add_bednets_for_population_and_births, archetype_seasonal_usage, add_simple_hs, add_scenario_specific_smc
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign
from malaria.reports.MalariaReport import add_summary_report, add_event_counter_report
from reports import add_burnin_reports, add_scenario_reports, summary_age_bins
from setup_sim import build_project_cb, set_ento_splines, burnin_setup
import pandas as pd

###################
# Run description #
###################
# Run scenarios that draw from burnins

##################################
# Core malaria config parameters #
##################################
from simtools.ModBuilder import ModFn
from sweeps import modfn_sweep_over_habitat_scale, modfn_sweep_over_scenarios, modfn_sweep_over_burnins

archetype = "Sahel"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files

num_years = 2
sim_duration = num_years * 365
cb.set_param("Simulation_Duration", sim_duration)

add_simple_hs(cb, 0.8)

# Distribute ITNs on first day
add_bednets_for_population_and_births(cb,
                                      coverage=0.7,
                                      start_day=1,
                                      seasonal_dependence=archetype_seasonal_usage[archetype],
                                      discard_config_type="default")


scenario_descriptions = {
    0: "no intervention",
    1: "regular SMC",
    2: "SMC + iver",
    3: "SMC + prim",
    4: "SMC + iver + prim"
}


def add_smc_variant(cb, scenario_num):
    '''

    :param cb:
    :param scenario_num:
    0 = no intervention.
    1 = regular SMC.
    2 = SMC + iver.
    3 = SMC + prim
    4 = SMC + iver + prim
    :return:
    '''
    if scenario_num == 0:
        pass
    else:
        add_scenario_specific_smc(cb, age_range="default")

    if scenario_num == 2 or scenario_num == 4:
        add_ivermectin(cb,
                       box_duration="WEEK",
                       start_days=[1], #Listening for drug delivery in other methods, then give this drug
                       trigger_condition_list=['Received_SMC'])

    if scenario_num == 3 or scenario_num == 4:
        add_drug_campaign(cb,
                          'MDA',
                          drug_code="PMQ",
                          start_days=[1],
                          trigger_condition_list=['Received_SMC'],
                          receiving_drugs_event_name='Received_Primaquine'
                          )

    return {"scenario_num": scenario_num,
            "scenario_description": scenario_descriptions[scenario_num]}


#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 10
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_burnins(archetype)
modlists.append(modlist)

modlist = [ModFn(add_smc_variant, s) for s in [0,1,2,3,4]]
modlists.append(modlist)


####################
# Reports and logs #
####################
add_summary_report(cb, age_bins=summary_age_bins, start=365, duration_days=sim_duration)
cb.set_param("Enable_Demographics_Reporting", 1)

events_to_count = [
    "Received_Treatment",
    "Received_Test",
    "Received_Campaign_Drugs",
    "Received_RCD_Drugs",
    "Received_SMC",
    "Received_Ivermectin",
    "Received_Primaquine"
]

events_to_count += ["Bednet_Discarded", "Bednet_Got_New_One", "Bednet_Using"]

add_event_counter_report(cb, event_trigger_list=events_to_count, duration=sim_duration)

cb.set_param("Enable_Default_Reporting", 1)


###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "sahel_smc_with_transmission_blocking"
comps_priority = "Normal"
# comps_priority = "Highest"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)
