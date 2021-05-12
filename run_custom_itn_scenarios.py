import numpy as np
from dtk.interventions.irs import add_IRS
from dtk.interventions.ivermectin import add_ivermectin
from dtk.vector.species import set_species_param

from interventions import add_burnin_historical_interventions, set_school_children_ips, add_scenario_specific_itns, \
    add_scenario_specific_healthseeking, add_scenario_specific_ipt, add_bednets_for_population_and_births, \
    archetype_seasonal_usage, default_bednet_age_usage, add_simple_hs
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from jsuresh_helpers.relative_time import month_times
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign, WaningEffectExponential
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

archetype = "Magude"
cb = build_project_cb(archetype=archetype)



##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files

cb.set_param("Simulation_Duration", 6*365)


old_net_usage = [
    0.9521528827448246,
    0.9968962224187727,
    0.9876766366776979,
    0.9268987891345297,
    0.8304148322138744,
    0.7233898293962878,
    0.6337381726270144,
    0.5848429165167919,
    0.5894569814803964,
    0.6463769214588317,
    0.7407568081902138,
    0.8479803643504683
]

# Correct net usage for fact that lots of biting happens indoors but before bedtime
new_net_usage = list(np.array(old_net_usage)*0.7)


very_low_discard_rates = {
    "Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
    "Expiration_Period_Exponential": 2500
}

def itn_scenario(cb, scenario_num):
    def burnin_draw(old_or_new):
        cb.set_param("Serialized_Population_Filenames", ["state-18250.dtk"])
        if old_or_new == "old":
            cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\magude_burnins_ento_comparison_no__20210511_023616\\c44\\69a\\820\\c4469a82-01b2-eb11-a2e3-c4346bcb7275\\output")
        elif old_or_new == "new":
            cb.set_param("Serialized_Population_Path", "\\\\internal.idm.ctr\\IDM\\Home\\jsuresh\\output\\magude_burnins_ento_comparison_no__20210511_023616\\c64\\69a\\820\\c6469a82-01b2-eb11-a2e3-c4346bcb7275\\output")

        # set ento
        if old_or_new == "old":
            set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.5)
            set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
            set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
            set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

            set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.9)
            set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
            set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
            set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        elif old_or_new == "new":
            set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.95)
            set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
            set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
            set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

            set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.6)
            set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
            set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
            set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")



    # Assume net goes from initial killing of 0.7 to 0.275 in 2 years (0.275 corresponds to 17% bioefficacy seen after 2 years)
    new_killing_config = WaningEffectExponential(Decay_Time_Constant=781, Initial_Effect=0.7)
    new_blocking_config = WaningEffectExponential(Decay_Time_Constant=2046, Initial_Effect=0.6)

    old_seasonal_usage = {"Times": month_times, "Values": old_net_usage}
    new_seasonal_usage = {"Times": month_times, "Values": new_net_usage}

    if scenario_num == 0:
        burnin_draw("old")

    elif scenario_num == 1:
        burnin_draw("old")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=old_seasonal_usage,
                                              discard_config_type="default",
                                              age_dependence=default_bednet_age_usage)

    elif scenario_num == 2:
        burnin_draw("new")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=old_seasonal_usage,
                                              discard_config_type="default",
                                              age_dependence=default_bednet_age_usage)

    elif scenario_num == 3:
        burnin_draw("new")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=new_seasonal_usage,
                                              discard_config_type="default",
                                              age_dependence=default_bednet_age_usage)

    elif scenario_num == 4:
        burnin_draw("new")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=new_seasonal_usage,
                                              discard_config_type="default",
                                              age_dependence=default_bednet_age_usage,
                                              killing_config=new_killing_config)

    elif scenario_num == 5:
        burnin_draw("new")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=new_seasonal_usage,
                                              discard_config_type="default",
                                              age_dependence=default_bednet_age_usage,
                                              killing_config=new_killing_config,
                                              blocking_config=new_blocking_config)

    elif scenario_num == 6:
        burnin_draw("new")
        add_bednets_for_population_and_births(cb, 0.7, start_day=11*30,
                                              seasonal_dependence=new_seasonal_usage,
                                              discard_config_type="very_low",
                                              age_dependence=default_bednet_age_usage,
                                              killing_config=new_killing_config,
                                              blocking_config=new_blocking_config)

    elif scenario_num == 7:
        burnin_draw("new")


    scenario_describe = {
        0: "Old ento, no ITNs",
        1: "Old ento, old ITNs",
        2: "New ento, old ITNs",
        3: "New ento, old ITNs but less effective coverage",
        4: "New ento, ITNs with less effective coverage and new killing",
        5: "New ento, ITNs with less effective coverage and new killing and blocking",
        6: "New ento, ITNs with less effective coverage and new killing and blocking and discard rates",
        7: "New ento, no ITNs"
    }
    return {"itn_scenario": scenario_num,
            "scenario_description": scenario_describe[scenario_num]}



#####################
# Experiment sweeps #
#####################

add_simple_hs(cb, 0.75)

# annual actellic spray
for y in range(6):
    spray_date = 9*30 + 365*y

    add_IRS(cb,
            start=spray_date,
            coverage_by_ages=[{'coverage': 0.75}],
            killing_config={
                "Initial_Effect": 0.9,
                "Decay_Time_Constant": 30,
                "Box_Duration": 210,
                "class": "WaningEffectBoxExponential"
            })


modlists = []

num_seeds = 5
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)


# modlist = [ModFn(itn_scenario, s) for s in [0,1,2,3,4,5,6]]
modlist = [ModFn(itn_scenario, s) for s in [0,7]] # no-ITN scenarios
modlists.append(modlist)


####################
# Reports and logs #
####################
add_summary_report(cb, age_bins=summary_age_bins, start=365)

events_to_count = [
    "Received_Treatment",
    "Received_IRS"
]

events_to_count += ["Bednet_Discarded", "Bednet_Got_New_One", "Bednet_Using"]

add_event_counter_report(cb, event_trigger_list=events_to_count)

cb.set_param("Enable_Default_Reporting", 1)


###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "magude_irs_exploration"
comps_priority = "Highest"
# comps_priority = "Highest"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)
