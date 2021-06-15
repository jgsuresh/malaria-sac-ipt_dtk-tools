import pandas as pd
import numpy as np

from interventions import add_scenario_specific_interventions
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign

from setup_sim import set_ento_splines, draw_from_serialized_file
from simtools.ModBuilder import ModFn


def modfn_sweep_over_habitat_scale(habitat_scale_array, archetype):
    modlist = [ModFn(set_ento_splines, hs, archetype) for hs in habitat_scale_array]
    return modlist

def modfn_sweep_over_scenarios(archetype, specific_scenarios_to_run=None):
    scenario_df = pd.read_csv("scenario_master_list.csv")
    scenario_df = scenario_df[scenario_df["archetype"]==archetype].reset_index(drop=True)

    if specific_scenarios_to_run == None:
        scenario_numbers = list(scenario_df["scenario_number"])
    else:
        scenario_numbers = specific_scenarios_to_run

    # scenario_numbers = scenario_numbers[:2] #TESTING ONLY

    modlist = [ModFn(add_scenario_specific_interventions, ns, archetype) for ns in scenario_numbers]
    return modlist

def modfn_sweep_over_burnins(archetype):
    burnin_df = pd.read_csv("burnins.csv")
    burnin_df = burnin_df[burnin_df["archetype"]==archetype]

    modlist = []
    for i, row in burnin_df.iterrows():
        modlist.append(ModFn(draw_from_serialized_file, dict(row)))

    return modlist

def modfn_sweep_over_timings(archetype, num_years=1):
    if archetype == "Southern":
        timings_df = pd.read_csv("southern_term_sweep_scenarios.csv")
    elif archetype == "Sahel":
        timings_df = pd.read_csv("sahel_term_sweep_scenarios.csv")
    elif archetype == "Central":
        timings_df = pd.read_csv("central_term_sweep_scenarios.csv")
    else:
        raise NotImplementedError

    scenario_numbers = list(timings_df["scenario_number"])

    # scenario_numbers = range(5) #TEST ONLY

    modlist = [ModFn(add_ipt_for_timing_sweep, ns, archetype, num_years) for ns in scenario_numbers]
    return modlist




#fixme not very elegant/general to other archetypes
def add_ipt_for_timing_sweep(cb, scenario_number, archetype, num_years=1):
    if archetype == "Southern":
        timings_df = pd.read_csv("southern_term_sweep_scenarios.csv")
    elif archetype == "Sahel":
        timings_df = pd.read_csv("sahel_term_sweep_scenarios.csv")
    elif archetype == "Central":
        timings_df = pd.read_csv("central_term_sweep_scenarios.csv")
    else:
        raise NotImplementedError

    scenario_dict = dict(timings_df[timings_df["scenario_number"]==scenario_number].reset_index(drop=True).iloc[0])

    for y in range(num_years):
        campaign_days = np.array([scenario_dict["term1_day"]+y*365,
                                  scenario_dict["term2_day"]+y*365,
                                  scenario_dict["term3_day"]+y*365])

        add_drug_campaign(cb,
                          campaign_type="MDA",
                          drug_code="DP",
                          start_days=list(campaign_days),
                          coverage=1,
                          ind_property_restrictions=[{"SchoolStatus": "AttendsSchool"}])

    return {"scenario_number": scenario_number}

    #fixme repetitions?