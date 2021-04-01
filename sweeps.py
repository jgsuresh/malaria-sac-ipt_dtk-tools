import pandas as pd
import numpy as np

from interventions import add_scenario_specific_interventions
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign

from setup_sim import set_ento_splines, draw_from_serialized_file
from simtools.ModBuilder import ModFn


def modfn_sweep_over_habitat_scale(habitat_scale_array, archetype):
    modlist = [ModFn(set_ento_splines, hs, archetype) for hs in habitat_scale_array]
    return modlist

def modfn_sweep_over_scenarios(archetype):
    scenario_df = pd.read_csv("scenario_master_list.csv")
    scenario_df = scenario_df[scenario_df["archetype"]==archetype].reset_index(drop=True)
    scenario_numbers = list(scenario_df["scenario_number"])

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

def modfn_sweep_over_timings(archetype):
    if archetype == "Southern":
        timings_df = pd.read_csv("southern_term_sweep_scenarios.csv")
        scenario_numbers = list(timings_df["scenario_number"])

        # scenario_numbers = range(5) #TEST ONLY

        modlist = [ModFn(add_ipt_for_timing_sweep, ns, archetype) for ns in scenario_numbers]
        return modlist

    elif archetype == "Sahel":
        timings_df = pd.read_csv("sahel_term_sweep_scenarios.csv")
        scenario_numbers = list(timings_df["scenario_number"])

        # scenario_numbers = range(5) #TEST ONLY

        modlist = [ModFn(add_ipt_for_timing_sweep, ns, archetype) for ns in scenario_numbers]
        return modlist

    else:
        raise NotImplementedError


#fixme not very elegant/general to other archetypes
def add_ipt_for_timing_sweep(cb, scenario_number, archetype):
    if archetype == "Southern":
        timings_df = pd.read_csv("southern_term_sweep_scenarios.csv")
    elif archetype == "Sahel":
        timings_df = pd.read_csv("sahel_term_sweep_scenarios.csv")
    else:
        raise NotImplementedError

    scenario_dict = dict(timings_df[timings_df["scenario_number"]==scenario_number].reset_index(drop=True).iloc[0])

    campaign_days = np.array([scenario_dict["term1_day"],
                              scenario_dict["term2_day"],
                              scenario_dict["term3_day"]])

    add_drug_campaign(cb,
                      campaign_type="MDA",
                      drug_code="DPP",
                      start_days=list(campaign_days),
                      coverage=1,
                      ind_property_restrictions=[{"SchoolStatus": "AttendsSchool"}])

    return {"scenario_number": scenario_number}

    #fixme repetitions?