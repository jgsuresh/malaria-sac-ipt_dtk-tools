import numpy as np
from dtk.interventions.ivermectin import add_ivermectin

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_scenario_specific_itns, \
    add_scenario_specific_healthseeking, add_scenario_specific_ipt, set_school_children_ips_for_complex_age_dist, \
    add_bednets_for_population_and_births, archetype_seasonal_usage, add_simple_hs
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

archetype = "Southern"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files

num_years = 20
sim_duration = num_years * 365
cb.set_param("Simulation_Duration", sim_duration)

set_school_children_ips_for_complex_age_dist(cb, sac_in_school_fraction=0.9, number_of_years=num_years)
add_simple_hs(cb, 0.8)

# Distribute ITNs every 3 years
for y in np.arange(0,20,3):
    dtk_start_day = y*365 + 1
    add_bednets_for_population_and_births(cb,
                                          coverage=0.7,
                                          start_day=dtk_start_day,
                                          seasonal_dependence=archetype_seasonal_usage[archetype],
                                          discard_config_type="default")



def add_long_term_ipt(cb, ipt_on):
    if ipt_on:
        term_days = [15,165,254]

        for y in range(num_years):
            for t in [1,2,3]:
                dtk_day = y*365 + term_days[t-1]

                add_drug_campaign(cb,
                                  campaign_type="MDA",
                                  drug_code="DP",
                                  start_days=[dtk_day],
                                  coverage=0.9,
                                  ind_property_restrictions=[{"SchoolStatus": "AttendsSchool"}],
                                  receiving_drugs_event_name="Received_Campaign_Drugs")
    else:
        pass

    return {"ipt_on": ipt_on}


#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 10
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_burnins(archetype)
modlists.append(modlist)

modlist = [ModFn(add_long_term_ipt, ipt_on) for ipt_on in [True,False]]
modlists.append(modlist)


####################
# Reports and logs #
####################
add_summary_report(cb, age_bins=summary_age_bins, start=365, duration_days=sim_duration)

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

comps_experiment_name = "southern_sac_ipt_long"
comps_priority = "AboveNormal"
# comps_priority = "Highest"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)
