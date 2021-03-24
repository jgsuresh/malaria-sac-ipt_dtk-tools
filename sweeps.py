import pandas as pd
from interventions import add_scenario_specific_interventions

from setup_sim import set_ento_splines
from simtools.ModBuilder import ModFn


def modfn_sweep_over_habitat_scale(habitat_scale_array, archetype):
    modlist = [ModFn(set_ento_splines, hs, archetype) for hs in habitat_scale_array]
    return modlist

def modfn_sweep_over_burnins(archetype):
    if archetype == "Southern":
        pass
    else:
        raise NotImplementedError

# as before, CSV of archetype, transmission level, and corresponding experiment id, and, most importantly, path


def modfn_sweep_over_scenarios(archetype):
    scenario_df = pd.read_csv("scenario_master_list.csv")
    scenario_df = scenario_df[scenario_df["archetype"]==archetype].reset_index(drop=True)
    scenario_numbers = list(scenario_df["scenario_number"])

    modlist = [ModFn(add_scenario_specific_interventions, ns, archetype) for ns in scenario_numbers]
    return modlist

def modfn_sweep_over_timings(archetype):
    timings_df = pd.read_csv()


    #fixme difference between a regular scenario and one of these sweeps:
    # no itns.  only one year.