# Put functions relating to interventions here

import pandas as pd
import numpy as np
from dtk.interventions.itn_age_season import add_ITN_age_season
from dtk.interventions.property_change import change_individual_property
from dtk.utils.Campaign.CampaignClass import OutbreakIndividual, BroadcastEvent, CampaignEvent, \
    StandardInterventionDistributionEventCoordinator, \
    StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum, MultiInterventionDistributor
from malaria.interventions.health_seeking import add_health_seeking
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign

from jsuresh_helpers.relative_time import month_times

default_bednet_age_usage = {'youth_cov': 0.65,
                            'youth_min_age': 5,
                            'youth_max_age': 20}

default_itn_discard_rates = {
    "Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
    "Expiration_Period_Mean_1": 260,
    "Expiration_Period_Mean_2": 2106,
    "Expiration_Period_Proportion_1": 0.6
}

flat_annual_itn_discard_rates = {
    "Expiration_Period_Distribution": "CONSTANT_DISTRIBUTION",
    "Expiration_Period_Constant": 365
}

discard_config = {
    "default": default_itn_discard_rates,
    "flat_annual": flat_annual_itn_discard_rates
}

archetype_list = ["Southern", "Central", "Eastern", "Coastal Western", "Sahel"]


sahel_seasonal_itn_use = [
    0.84,
    0.71,
    0.74,
    0.55,
    0.56,
    0.62,
    0.85,
    0.94,
    0.98,
    1,
    0.97,
    0.94
]

coastal_western_seasonal_itn_use = [
    1,
    0.76,
    0.64,
    0.65,
    0.55,
    0.79,
    0.83,
    0.97,
    0.89,
    0.92,
    0.89,
    0.97
]

eastern_seasonal_itn_use = [
    0.88,
    0.71,
    0.83,
    1,
    0.86,
    0.85,
    0.81,
    0.75,
    0.75,
    0.5,
    0.94,
    0.94
]

central_seasonal_itn_use = [
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82,
    0.82
]

archetype_seasonal_usage = {
    "Southern": {'min_cov': 0.5, 'max_day': 60},
    "Sahel": {"Times": month_times, "Values": sahel_seasonal_itn_use},
    "Coastal Western": {"Times": month_times, "Values": coastal_western_seasonal_itn_use},
    "Central": {"Times": month_times, "Values": central_seasonal_itn_use},
    "Eastern": {"Times": month_times, "Values": eastern_seasonal_itn_use}
}


def add_bednets_for_population_and_births(cb, coverage, start_day=1, seasonal_dependence=None, discard_config_type="default"):
    if seasonal_dependence is None:
        seasonal_dependence = {}

    # regular_bednet_distribution
    add_ITN_age_season(cb,
                       birth_triggered=False,
                       start=start_day,
                       age_dependence=default_bednet_age_usage,
                       demographic_coverage=coverage,
                       seasonal_dependence=seasonal_dependence,
                       discard_times=discard_config[discard_config_type])

    # birth_triggered_bednet_distribution
    add_ITN_age_season(cb,
                       birth_triggered=True,
                       start=start_day,
                       age_dependence=default_bednet_age_usage,
                       demographic_coverage=coverage,
                       seasonal_dependence=seasonal_dependence,
                       discard_times=discard_config[discard_config_type])




def add_burnin_historical_bednets(cb, archetype="Southern", start_year=1970):
    # at certain times, add bednets with different coverages
    # these bednet distributions are each for 1 year, then expire (not normal expiration)
    if archetype == "Southern":
        # open CSV
        df = pd.read_csv("southern_historical_itn.csv")
        for index, row in df.iterrows():
            # Assume 50 year burnin, so 2000 is year 30
            campaign_start_day = int((row["year"]-start_year)*365)

            add_bednets_for_population_and_births(cb,
                                                  coverage=row["cov_all"],
                                                  start_day=campaign_start_day,
                                                  seasonal_dependence=archetype_seasonal_usage[archetype],
                                                  discard_config_type="flat_annual")

    else:
        raise NotImplementedError



def add_simple_hs(cb, u5_hs_rate, o5_hs_rate=-1, start_day=1, duration=-1):
    if o5_hs_rate == -1:
        o5_hs_rate = u5_hs_rate * 0.5

    target_list = [{'trigger': 'NewClinicalCase',
                    'coverage': u5_hs_rate,
                    'agemin': 0,
                    'agemax': 5,
                    'seek': 1,
                    'rate': 0.3},
                   {'trigger': 'NewClinicalCase',
                    'coverage': o5_hs_rate,
                    'agemin': 5,
                    'agemax': 100,
                    'seek': 1,
                    'rate': 0.3},
                   {'trigger': 'NewSevereCase',
                    'coverage': 0.9,
                    'agemin': 0,
                    'agemax': 5,
                    'seek': 1,
                    'rate': 0.5},
                   {'trigger': 'NewSevereCase',
                    'coverage': 0.8,
                    'agemin': 5,
                    'agemax': 100,
                    'seek': 1,
                    'rate': 0.5}]

    add_health_seeking(cb,
                       start_day=start_day,
                       targets=target_list,
                       drug=['Artemether', 'Lumefantrine'],
                       duration=duration)

def add_burnin_historical_healthseeking(cb, archetype="Southern", start_year=1970):
    # at certain times, add HS campaign events with different coverages
    # these campign events are each for 1 year, then expire (not normal expiration)\

    if archetype == "Southern":
        # open CSV
        df = pd.read_csv("southern_historical_hs.csv")
        for index, row in df.iterrows():
            # Assume 50 year burnin, so 2000 is year 30
            campaign_start_day = int((row["year"]-start_year)*365)

            add_simple_hs(cb,
                          u5_hs_rate=row["cov_newclin_youth"],
                          start_day=campaign_start_day,
                          duration=365)

    else:
        raise NotImplementedError




    pass




def add_burnin_historical_interventions(cb, archetype):
    add_burnin_historical_healthseeking(cb, archetype)
    add_burnin_historical_bednets(cb, archetype)


def add_scenario_specific_itns(cb, itn_coverage_level, archetype):
    if itn_coverage_level == "default":
        dtk_coverage = 0.7
    elif itn_coverage_level == "high":
        dtk_coverage = 0.9
    else:
        raise NotImplementedError

    add_bednets_for_population_and_births(cb,
                                          dtk_coverage,
                                          seasonal_dependence=archetype_seasonal_usage[archetype],
                                          discard_config_type="default")


def add_scenario_specific_healthseeking(cb, hs_rate):
    if hs_rate == "default":
        u5_hs_rate = 0.8
    elif hs_rate == "low":
        u5_hs_rate = 0.6
    else:
        raise NotImplementedError

    add_simple_hs(cb, u5_hs_rate)

def add_scenario_specific_ipt(cb, scenario_dict, archetype):
    # scenario dict has drug_type,screen_type,interval,school_coverage
    if scenario_dict["screen_type"] == "IPT":
        dtk_campaign_type = "MDA"
    elif scenario_dict["screen_type"] == "IST":
        dtk_campaign_type = "MSAT"
    else:
        raise NotImplementedError

    drug_code = scenario_dict["drug_type"]
    if drug_code == "SPAQ":
        drug_code = "SPA"

    # timing:
    timings_df = pd.read_csv("ipt_timings.csv")
    timings_df = timings_df[np.logical_and(timings_df["archetype"]==archetype,
                                           timings_df["interval"]==scenario_dict["interval"])].reset_index(drop=True)
    campaign_days = np.array(timings_df["day"])

    # Assuming that we do the same thing for 2 years:
    campaign_days = np.append(campaign_days, campaign_days+365)

    add_drug_campaign(cb,
                      campaign_type=dtk_campaign_type,
                      drug_code=drug_code,
                      start_days=list(campaign_days),
                      coverage=scenario_dict["school"],
                      ind_property_restrictions=[{"SchoolStatus": "AttendsSchool"}],
                      diagnostic_type='BLOOD_SMEAR_PARASITES',
                      diagnostic_threshold=0)

    #fixme repetitions?


def add_scenario_specific_interventions(cb, scenario_number, archetype="Southern"):
    # open scenario df and get this number
    scenario_df = pd.read_csv("scenario_master_list.csv")
    scenario_dict = dict(scenario_df[np.logical_and(scenario_df["archetype"]==archetype,
                                                    scenario_df["scenario_number"]==scenario_number)])

    set_school_children_ips(cb)

    add_scenario_specific_itns(cb, scenario_dict["itn_coverage"], archetype=archetype)
    add_scenario_specific_healthseeking(cb, scenario_dict["hs_rate"])
    add_scenario_specific_ipt(cb, scenario_dict, archetype)

    return scenario_dict


def set_school_children_ips(cb, sac_in_school_fraction=0.9):
    # Initial setup
    change_individual_property(cb,
                               target_property_name="SchoolStatus",
                               target_property_value="AttendsSchool",
                               target_group={"agemin": 5, "agemax": 16},
                               coverage=sac_in_school_fraction,
                               daily_prob=1,
                               max_duration=1,
                               start_day=1)

    # Each September 1st, add in new kids and remove old ones:
    for school_start_day in [244, 365+244]:
        change_individual_property(cb,
                                   target_property_name="SchoolStatus",
                                   target_property_value="AttendsSchool",
                                   target_group={"agemin": 5, "agemax": 6},
                                   coverage=sac_in_school_fraction,
                                   daily_prob=1,
                                   max_duration=1,
                                   start_day=school_start_day)

        change_individual_property(cb,
                                   target_property_name="SchoolStatus",
                                   target_property_value="DoesNotAttendSchool",
                                   target_group={"agemin": 16, "agemax": 17},
                                   coverage=1,
                                   daily_prob=1,
                                   max_duration=1,
                                   start_day=school_start_day)


def set_school_children_ips_TEST(cb):
    # Initial setup
    change_individual_property(cb,
                               target_property_name="SchoolStatus",
                               target_property_value="AttendsSchool",
                               target_group={"agemin": 5, "agemax": 16},
                               coverage=0.9,
                               daily_prob=1,
                               max_duration=1,
                               start_day=1)

    # school_start_day = 244
    # change_individual_property(cb,
    #                            target_property_name="SchoolStatus",
    #                            target_property_value="AttendsSchool",
    #                            target_group={"agemin": 5, "agemax": 6},
    #                            daily_prob=1,
    #                            max_duration=1,
    #                            start_day=school_start_day)
    #
    # change_individual_property(cb,
    #                            target_property_name="SchoolStatus",
    #                            target_property_value="DoesNotAttendSchool",
    #                            target_group={"agemin": 16, "agemax": 17},
    #                            daily_prob=1,
    #                            max_duration=1,
    #                            start_day=school_start_day)



def recurring_outbreak_as_importation_josh(cb, outbreak_fraction=0.01, repetitions=-1, tsteps_btwn=365, target='Everyone', start_day=0, strain=(0,0), nodes={"class": "NodeSetAll"}, outbreak_source="PrevalenceIncrease", property_restrictions=[]):
    """
    Add introduction of new infections to the campaign using the
    **OutbreakIndividual** class. Outbreaks can be recurring.

    Args:
        cb: The The :py:class:`DTKConfigBuilder
            <dtk.utils.core.DTKConfigBuilder>` containing the campaign
            configuration.
        outbreak_fraction: The fraction of people infected by the outbreak (
            **Demographic_Coverage** parameter).
        repetitions: The number of times to repeat the intervention.
        tsteps_btwn_:  The number of time steps between repetitions.
        target: The individuals to target with the intervention. To
            restrict by age, provide a dictionary of {'agemin' : x, 'agemax' :
            y}. Default is targeting everyone.
        start_day: The day on which to start distributing the intervention
            (**Start_Day** parameter).
        strain: A two-element tuple defining (Antigen, Genome).
        nodes: A dictionary defining the nodes to apply this intervention to
            (**Nodeset_Config** parameter).
        outbreak_source: The source of the outbreak.

    Returns:
        A dictionary holding the fraction and the time steps between events.

        Example:
        ::

            cb = DTKConfigBuilder.from_defaults(sim_example)
            recurring_outbreak(cb, outbreak_fraction=0.005, repetitions=3,
                               tsteps_btwn=30, target={"agemin": 1, "agemax": 5},
                               start_day=0, strain=("A", "H2N2"),
                               nodes={"class": "NodeSetAll"},
                               outbreak_source="PrevalenceIncrease")

    """

    intervention_list = [OutbreakIndividual(Antigen=strain[0], Genome=strain[1]),
                         BroadcastEvent(Broadcast_Event="InfectionDropped")
                         ]

    outbreak_event = CampaignEvent(
        Start_Day=start_day,
        Event_Coordinator_Config=StandardInterventionDistributionEventCoordinator(
            # Number_Distributions=-1, #DanB said this doesn't do anything
            Number_Repetitions=repetitions,
            Timesteps_Between_Repetitions=tsteps_btwn,
            Property_Restrictions=property_restrictions,
            Target_Demographic=StandardInterventionDistributionEventCoordinator_Target_Demographic_Enum[target],
            Demographic_Coverage=outbreak_fraction,
            Intervention_Config=MultiInterventionDistributor(Intervention_List=intervention_list)
        ),
        Nodeset_Config=nodes
    )

    cb.add_event(outbreak_event)
    return {'outbreak_fraction': outbreak_fraction,
            'tsteps_btwn': tsteps_btwn}



def import_infections_through_outbreak(cb, days_between_outbreaks=365, start_day=1,
                                       num_infections=1,
                                       underlying_pop=5000):

    outbreak_fraction = num_infections/underlying_pop
    property_restrictions = []

    if outbreak_fraction > 0:
        recurring_outbreak_as_importation_josh(cb,
                                               outbreak_fraction=outbreak_fraction,
                                               tsteps_btwn=days_between_outbreaks,
                                               property_restrictions=property_restrictions,
                                               start_day=start_day)

    return {"infections_per_importation": num_infections,
            "days_between_importations": days_between_outbreaks}


def seasonal_daily_importations(cb, total_importations_per_year, archetype="Southern"):
    if archetype == "Southern":
        seasonal_spline = pd.read_csv("southern_new_infection_spline.csv")
        spline_sum = np.sum(seasonal_spline["new_infections"])
        rescale_factor = total_importations_per_year/spline_sum

        for d in np.arange(365):
            import_infections_through_outbreak(cb,
                                               days_between_outbreaks=365,
                                               start_day=d,
                                               num_infections=rescale_factor*seasonal_spline["new_infections"].iloc[d])

        return {"total_importations_per_year": total_importations_per_year}

    else:
        raise NotImplementedError