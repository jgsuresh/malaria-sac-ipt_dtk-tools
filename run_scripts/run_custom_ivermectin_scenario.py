import numpy as np
from dtk.interventions.ivermectin import add_ivermectin

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_scenario_specific_itns, \
    add_scenario_specific_healthseeking, add_scenario_specific_ipt
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

cb.set_param("Simulation_Duration", 2*365)

scenario_number = 34

# open scenario df and get this number
scenario_df = pd.read_csv("scenario_master_list.csv")
scenario_dict = scenario_df[np.logical_and(scenario_df["archetype"]==archetype,
                                           scenario_df["scenario_number"]==scenario_number)].to_dict("records")[0]

set_school_children_ips(cb,
                        sac_in_school_fraction=(1-scenario_dict["out_of_school_rate"]),
                        age_dependence="complex",
                        target_age_range=scenario_dict["target_age_range"])

add_scenario_specific_itns(cb, scenario_dict["itn_coverage"], archetype=archetype)
add_scenario_specific_healthseeking(cb, scenario_dict["hs_rate"])

def add_ipt_with_iver_skipping_one_term(cb, term_to_skip):
    term_days = [15,165,254]

    for y in [0,1]:
        for t in [1,2,3]:
            dtk_day = y*365 + term_days[t-1]

            add_drug_campaign(cb,
                              campaign_type="MDA",
                              drug_code="DP",
                              start_days=[dtk_day],
                              coverage=scenario_dict["within_school_coverage"],
                              ind_property_restrictions=[{"SchoolStatus": "AttendsSchool"}],
                              diagnostic_type='BLOOD_SMEAR_PARASITES',
                              diagnostic_threshold=0,
                              receiving_drugs_event_name="Received_Campaign_Drugs_Term_{}".format(t))

    terms_with_iver = [1,2,3]
    terms_with_iver.remove(term_to_skip)
    iver_trigger_list = ["Received_Campaign_Drugs_Term_{}".format(t) for t in terms_with_iver]

    add_ivermectin(cb,
                   box_duration="WEEK",
                   start_days=[1], #Listening for drug delivery in other methods, then give this drug
                   trigger_condition_list=iver_trigger_list)

    return {"term_skipped": term_to_skip}


#####################
# Experiment sweeps #
#####################
modlists = []

num_seeds = 100
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

modlist = modfn_sweep_over_burnins(archetype)
modlists.append(modlist)

# modlist = modfn_sweep_over_scenarios(archetype, specific_scenarios_to_run=[13,30,34,35,36])
# modlists.append(modlist)
modlist = [ModFn(add_ipt_with_iver_skipping_one_term, t) for t in [1,2,3]]
modlists.append(modlist)


####################
# Reports and logs #
####################
add_summary_report(cb, age_bins=summary_age_bins, start=365)

events_to_count = [
    "Received_Treatment",
    "Received_Test",
    "Received_Campaign_Drugs_Term_1",
    "Received_Campaign_Drugs_Term_2",
    "Received_Campaign_Drugs_Term_3",
    "Received_RCD_Drugs",
    "Received_SMC",
    "Received_Ivermectin",
    "Received_Primaquine"
]

events_to_count += ["Bednet_Discarded", "Bednet_Got_New_One", "Bednet_Using"]

add_event_counter_report(cb, event_trigger_list=events_to_count)

cb.set_param("Enable_Default_Reporting", 1)


###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "southern_sac_ipt_iver_withheld_from_term"
comps_priority = "AboveNormal"
# comps_priority = "Highest"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)
