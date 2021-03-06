import os

from dtk.interventions.outbreakindividual import recurring_outbreak
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder

from dtk.vector.species import set_species, set_species_param
from interventions import add_burnin_historical_interventions, seasonal_daily_importations

from jsuresh_helpers.running_dtk import set_executable
from jsuresh_helpers.windows_filesystem import get_dropbox_location
from jsuresh_helpers.relative_time import month_times
from malaria import immunity, infection, symptoms

dropbox_folder = get_dropbox_location()
input_folder = dropbox_folder + "projects/school_aged_children_ipt/sims/"
bin_folder = input_folder + "bin/malaria_ongoing_build_245"


def set_ento_splines(cb, habitat_scale, archetype="Southern"):
    if archetype == "Southern":
        arab_scale = habitat_scale
        funest_scale = arab_scale-0.8

        set_species_param(cb,
                          'funestus',
                          "Larval_Habitat_Types",
                          {"LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.13, 0.33, 1., 0.67, 0.67, 0.67, 0.33, 0.33, 0.2, 0.13, 0.067, 0.067]
                              },
                              "Max_Larval_Capacity": 10**funest_scale
                          }})

        set_species_param(cb,
                          'arabiensis',
                          'Larval_Habitat_Types', {
                              "LINEAR_SPLINE": {
                                  "Capacity_Distribution_Number_Of_Years": 1,
                                  "Capacity_Distribution_Over_Time": {
                                      "Times": month_times,
                                      "Values": [0.6, 0.8, 1.0, 0.9, 0.1, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.05]
                                  },
                                  "Max_Larval_Capacity": 10**arab_scale
                              },
                              "CONSTANT": 10**4.9
                          })
        return_dict = {"hab_scale": habitat_scale}

    elif archetype == "Sahel":
        set_species_param(cb,
                          'gambiae',
                          "Larval_Habitat_Types",
                          {"LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                              },
                              "Max_Larval_Capacity": 10**habitat_scale
                          }})
        return_dict = {"hab_scale": habitat_scale}

    elif archetype == "Central":
        # Amelia's spline setup
        # x_overall_amelia = 63.1
        #
        # set_species_param(cb,
        #                   'gambiae',
        #                   "Larval_Habitat_Types",
        #                   {"CONSTANT": 40000000*x_overall_amelia,
        #                    "TEMPORARY_RAINFALL": 360000000*x_overall_amelia,
        #                   "LINEAR_SPLINE": {
        #                       "Capacity_Distribution_Number_Of_Years": 1,
        #                       "Capacity_Distribution_Over_Time": {
        #                           "Times": month_times,
        #                           "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
        #                       },
        #                       "Max_Larval_Capacity": 10**habitat_scale
        #                   }}
        #                   )
        #
        # set_species_param(cb,
        #                   'funestus',
        #                   "Larval_Habitat_Types",
        #                   {"WATER_VEGETATION": 400000000*x_overall_amelia,
        #                    "LINEAR_SPLINE": {
        #                        "Capacity_Distribution_Number_Of_Years": 1,
        #                        "Capacity_Distribution_Over_Time": {
        #                            "Times": month_times,
        #                            "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
        #                        },
        #                        "Max_Larval_Capacity": 10**habitat_scale
        #                    }}
        #                   )

        gamb_scale = habitat_scale
        funest_scale = gamb_scale-1.03 # Calculated for funestus to be ~5% of all mosquitos

        set_species_param(cb,
                          'gambiae',
                          "Larval_Habitat_Types",
                          {"LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.51, 0.42, 0.52, 0.66, 0.86, 0.92, 0.82, 0.75, 0.84, 0.99, 1.0, 0.77]
                              },
                              "Max_Larval_Capacity": 10**gamb_scale
                          }})

        set_species_param(cb,
                          'funestus',
                          "Larval_Habitat_Types",
                          {"LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.87, 0.82, 0.85, 0.9, 0.95, 0.93, 0.89, 0.87, 0.87, 0.94, 1.0, 0.97]
                              },
                              "Max_Larval_Capacity": 10**funest_scale
                          }})

        return_dict = {"hab_scale": habitat_scale}

    elif archetype == "Eastern":
        # Amelia's spline setup
        x_overall_amelia = 63.1

        set_species_param(cb,
                          'arabiensis',
                          "Larval_Habitat_Types",
                          {"CONSTANT": 40000000*x_overall_amelia,
                           "TEMPORARY_RAINFALL": 360000000*x_overall_amelia,
                           "LINEAR_SPLINE": {
                               "Capacity_Distribution_Number_Of_Years": 1,
                               "Capacity_Distribution_Over_Time": {
                                   "Times": month_times,
                                   "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                               },
                               "Max_Larval_Capacity": 10**habitat_scale
                           }}
                          )

        set_species_param(cb,
                          'gambiae',
                          "Larval_Habitat_Types",
                          {"CONSTANT": 40000000*x_overall_amelia,
                           "TEMPORARY_RAINFALL": 360000000*x_overall_amelia,
                          "LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                              },
                              "Max_Larval_Capacity": 10**habitat_scale
                          }}
                          )

        set_species_param(cb,
                          'funestus',
                          "Larval_Habitat_Types",
                          {"WATER_VEGETATION": 400000000*x_overall_amelia,
                           "LINEAR_SPLINE": {
                               "Capacity_Distribution_Number_Of_Years": 1,
                               "Capacity_Distribution_Over_Time": {
                                   "Times": month_times,
                                   "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                               },
                               "Max_Larval_Capacity": 10**habitat_scale
                           }}
                          )

        return_dict = {"hab_scale": habitat_scale}

    elif archetype == "Coastal Western":
        # Amelia's spline setup
        x_overall_amelia = 63.1

        set_species_param(cb,
                          'arabiensis',
                          "Larval_Habitat_Types",
                          {"CONSTANT": 40000000*x_overall_amelia,
                           "TEMPORARY_RAINFALL": 360000000*x_overall_amelia,
                           "LINEAR_SPLINE": {
                               "Capacity_Distribution_Number_Of_Years": 1,
                               "Capacity_Distribution_Over_Time": {
                                   "Times": month_times,
                                   "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                               },
                               "Max_Larval_Capacity": 10**habitat_scale
                           }}
                          )


        set_species_param(cb,
                          'gambiae',
                          "Larval_Habitat_Types",
                          {"CONSTANT": 40000000*x_overall_amelia,
                           "TEMPORARY_RAINFALL": 360000000*x_overall_amelia,
                           "LINEAR_SPLINE": {
                               "Capacity_Distribution_Number_Of_Years": 1,
                               "Capacity_Distribution_Over_Time": {
                                   "Times": month_times,
                                   "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                               },
                               "Max_Larval_Capacity": 10**habitat_scale
                           }}
                          )

        set_species_param(cb,
                          'funestus',
                          "Larval_Habitat_Types",
                          {"WATER_VEGETATION": 400000000*x_overall_amelia,
                           "LINEAR_SPLINE": {
                               "Capacity_Distribution_Number_Of_Years": 1,
                               "Capacity_Distribution_Over_Time": {
                                   "Times": month_times,
                                   "Values": [0.086, 0.023, 0.034, 0.0029, 0.077, 0.23, 0.11, 1., 0.19, 0.19, 0.074, 0.06]
                               },
                               "Max_Larval_Capacity": 10**habitat_scale
                           }}
                          )
        return_dict = {"hab_scale": habitat_scale}

    elif archetype == "Magude":
        arab_scale = habitat_scale
        funest_scale = arab_scale-0.56

        set_species_param(cb,
                          'funestus',
                          "Larval_Habitat_Types",
                          {"LINEAR_SPLINE": {
                              "Capacity_Distribution_Number_Of_Years": 1,
                              "Capacity_Distribution_Over_Time": {
                                  "Times": month_times,
                                  "Values": [0.009, 0.438, 0.005, 0.088, 0.049, 1.000, 0.023, 0.170, 0.015, 0.008, 0.376, 0.193]
                              },
                              "Max_Larval_Capacity": 10**funest_scale
                          }})

        set_species_param(cb,
                          'arabiensis',
                          'Larval_Habitat_Types', {
                              "LINEAR_SPLINE": {
                                  "Capacity_Distribution_Number_Of_Years": 1,
                                  "Capacity_Distribution_Over_Time": {
                                      "Times": month_times,
                                      "Values": [0.005, 0.119, 1.000, 0.069, 0.184, 0.203, 0.486, 0.157, 0.149, 0.185, 0.119, 0.011]
                                  },
                                  "Max_Larval_Capacity": 10**arab_scale
                              },
                              "CONSTANT": 10**4.9
                          })
        return_dict = {"hab_scale": habitat_scale}

    else:
        raise NotImplementedError

    return return_dict


def set_ento(cb, archetype="Southern"):

    if archetype == "Southern":
        set_species(cb, ["arabiensis", "funestus"])

        set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.5)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.9)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif archetype == "Sahel":
        set_species(cb, ["gambiae"])

        set_species_param(cb, 'gambiae', "Indoor_Feeding_Fraction", 0.9)
        set_species_param(cb, 'gambiae', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'gambiae', 'Anthropophily', 0.65)
        set_species_param(cb, 'gambiae', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif archetype == "Central":
        set_species(cb, ["gambiae", "funestus"])

        set_species_param(cb, 'gambiae', "Indoor_Feeding_Fraction", 0.5)
        set_species_param(cb, 'gambiae', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'gambiae', 'Anthropophily', 0.85)
        set_species_param(cb, 'gambiae', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.5)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif archetype == "Eastern":
        set_species(cb, ["gambiae", "funestus", "arabiensis"])

        set_species_param(cb, 'gambiae', "Indoor_Feeding_Fraction", 0.85)
        set_species_param(cb, 'gambiae', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'gambiae', 'Anthropophily', 0.85)
        set_species_param(cb, 'gambiae', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'arabiensis', "Indoor_Feeding_Fraction", 0.5)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.7) # Motivated by Uganda Vectorlink 2019
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif archetype == "Coastal Western":
        set_species(cb, ["gambiae", "funestus", "arabiensis"])

        set_species_param(cb, 'gambiae', "Indoor_Feeding_Fraction", 0.85)
        set_species_param(cb, 'gambiae', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'gambiae', 'Anthropophily', 0.8) # Slightly tuned down - Nigeria Vectorlink 2019
        set_species_param(cb, 'gambiae', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'arabiensis', "Indoor_Feeding_Fraction", 0.5)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.85)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif archetype == "Magude":
        set_species(cb, ["arabiensis", "funestus"])

        set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.95)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.6)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")


    else:
        raise NotImplementedError

    set_ento_splines(cb, habitat_scale=1, archetype=archetype)



def build_project_cb(archetype="Southern"):
    # cb = DTKConfigBuilder.from_defaults("MALARIA_SIM")
    # add_params_csv_to_dtk_config_builder(cb, params_csv_filename)
    cb = basic_gridded_config_builder(archetype=archetype)

    set_executable(cb, bin_folder)
    cb.set_input_files_root(input_folder)

    set_input_files(cb, archetype=archetype)
    set_ento(cb, archetype=archetype)

    return cb

def set_input_files(cb, archetype="Southern"):
    if archetype == "Southern":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_southern.json"],
            "Climate_Model": "CLIMATE_CONSTANT",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27
            # "Air_Temperature_Filename": "dtk_simulation_input/climate/southern/Zambia_30arcsec_air_temperature_daily.bin",
            # "Land_Temperature_Filename": "dtk_simulation_input/climate/southern/Zambia_30arcsec_air_temperature_daily.bin",
            # "Rainfall_Filename": "dtk_simulation_input/climate/southern/Zambia_30arcsec_rainfall_daily.bin",
            # "Relative_Humidity_Filename": "dtk_simulation_input/climate/southern/Zambia_30arcsec_relative_humidity_daily.bin"
        })
    elif archetype == "Sahel":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_sahel.json"],
            "Climate_Model": "CLIMATE_CONSTANT",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27
            # "Air_Temperature_Filename": "dtk_simulation_input/climate/sahel/Burkina Faso_30arcsec_air_temperature_daily.bin",
            # "Land_Temperature_Filename": "dtk_simulation_input/climate/sahel/Burkina Faso_30arcsec_air_temperature_daily.bin",
            # "Rainfall_Filename": "dtk_simulation_input/climate/sahel/Burkina Faso_30arcsec_rainfall_daily.bin",
            # "Relative_Humidity_Filename": "dtk_simulation_input/climate/sahel/Burkina Faso_30arcsec_relative_humidity_daily.bin"
        })
    elif archetype == "Central":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_central.json"],
            "Climate_Model": "CLIMATE_CONSTANT",
            # "Climate_Model": "CLIMATE_BY_DATA",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27,
            "Air_Temperature_Filename": "dtk_simulation_input/climate/central/DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin",
            "Land_Temperature_Filename": "dtk_simulation_input/climate/central/DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin",
            "Rainfall_Filename": "dtk_simulation_input/climate/central/DemocraticRepublicOfTheCongo_30arcsec_rainfall_daily.bin",
            "Relative_Humidity_Filename": "dtk_simulation_input/climate/central/DemocraticRepublicOfTheCongo_30arcsec_relative_humidity_daily.bin"
        })

    elif archetype == "Eastern":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_eastern.json"],
            # "Climate_Model": "CLIMATE_CONSTANT",
            "Climate_Model": "CLIMATE_BY_DATA",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27,
            "Air_Temperature_Filename": "dtk_simulation_input/climate/eastern/Ethiopia_30arcsec_air_temperature_daily.bin",
            "Land_Temperature_Filename": "dtk_simulation_input/climate/eastern/Ethiopia_30arcsec_air_temperature_daily.bin",
            "Rainfall_Filename": "dtk_simulation_input/climate/eastern/Ethiopia_30arcsec_rainfall_daily.bin",
            "Relative_Humidity_Filename": "dtk_simulation_input/climate/eastern/Ethiopia_30arcsec_relative_humidity_daily.bin"
        })

    elif archetype == "Coastal Western":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_coastal_western.json"],
            # "Climate_Model": "CLIMATE_CONSTANT",
            "Climate_Model": "CLIMATE_BY_DATA",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27,
            "Air_Temperature_Filename": "dtk_simulation_input/climate/coastal_western/Nigeria_30arcsec_air_temperature_daily.bin",
            "Land_Temperature_Filename": "dtk_simulation_input/climate/coastal_western/Nigeria_30arcsec_air_temperature_daily.bin",
            "Rainfall_Filename": "dtk_simulation_input/climate/coastal_western/Nigeria_30arcsec_rainfall_daily.bin",
            "Relative_Humidity_Filename": "dtk_simulation_input/climate/coastal_western/Nigeria_30arcsec_relative_humidity_daily.bin"
        })

    elif archetype == "Magude":
        cb.update_params({
            "Demographics_Filenames": ["dtk_simulation_input/demo_southern.json"],
            "Climate_Model": "CLIMATE_CONSTANT",
            "Base_Air_Temperature": 27,
            "Base_Land_Temperature": 27
        })

    else:
        raise NotImplementedError

def basic_gridded_config_builder(archetype="Southern"):
    cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

    cb.update_params(immunity.params)
    cb.update_params(infection.params)
    cb.update_params(symptoms.params)

    cb.update_params({
        'Antigen_Switch_Rate': pow(10, -9.116590124),
        'Base_Gametocyte_Production_Rate': 0.06150582,
        'Base_Gametocyte_Mosquito_Survival_Rate': 0.002011099,
        'Falciparum_MSP_Variants': 32,
        'Falciparum_Nonspecific_Types': 76,
        'Falciparum_PfEMP1_Variants': 1070,
        'Gametocyte_Stage_Survival_Rate': 0.588569307,
        'MSP1_Merozoite_Kill_Fraction': 0.511735322,
        'Max_Individual_Infections': 3,
        'Nonspecific_Antigenicity_Factor': 0.415111634
    })

    cb.update_params({
        "Climate_Model": "CLIMATE_BY_DATA",
        "Migration_Model": "NO_MIGRATION",
        "Enable_Immunity_Distribution": 0,
        "Enable_Immunity_Initialization_Distribution": 0,
        "Immunity_Initialization_Distribution_Type": "DISTRIBUTION_OFF",
        "Enable_Demographics_Risk": 1
    })

    cb.update_params({
        "Disable_IP_Whitelist": 1,
        "Enable_Demographics_Other": 1,
        "Enable_Demographics_Builtin": 0,
        "Valid_Intervention_States": [],
        "Report_Detection_Threshold_PfHRP2": 40.0,
        "Report_Detection_Threshold_Blood_Smear_Parasites": 0,
        "Parasite_Smear_Sensitivity": 0.025,
        "Report_Detection_Threshold_True_Parasite_Density": 40,
        "Birth_Rate_Dependence": "FIXED_BIRTH_RATE", # Match demographics file for constant population size (with exponential age distribution)
        "Enable_Nondisease_Mortality": 1,
    })

    # Intervention events
    intervene_events_list = ["Bednet_Got_New_One","Bednet_Using","Bednet_Discarded"]
    full_custom_events_list = [
        "Bednet_Got_New_One",
        "Bednet_Using",
        "Bednet_Discarded",
        "Received_Treatment",
        "Received_Campaign_Drugs",
        "Received_RCD_Drugs",
        "Received_Test",
        "Received_SMC",
        "Took_Dose",
        "InfectionDropped",
        "Received_Ivermectin",
        "Received_Primaquine",
        "Received_Campaign_Drugs_Term_1",
        "Received_Campaign_Drugs_Term_2",
        "Received_Campaign_Drugs_Term_3"
    ]
    cb.set_param("Custom_Individual_Events", full_custom_events_list)


    cb.update_params({
        "Report_Event_Recorder": 0,
        "Report_Event_Recorder_Ignore_Events_In_List": 0,
        # "Listed_Events": full_custom_events_list, #intervene_events_list
        "Report_Event_Recorder_Events": full_custom_events_list #intervene_events_list
    })


    # Basic entomology
    set_ento(cb, archetype=archetype) # I think there just needs to be something set for now

    return cb

def burnin_setup(cb, archetype):
    cb.set_param("Simulation_Duration", 50*365)
    cb.set_param("Serialization_Type", "TIMESTEP")
    cb.set_param("Serialization_Time_Steps", [50 * 365])
    cb.set_param("Serialization_Precision", "REDUCED")
    add_burnin_historical_interventions(cb, archetype=archetype)
    # recurring_outbreak(cb, outbreak_fraction=0.005)
    seasonal_daily_importations(cb, 25)

# def scenario_setup(cb,archetype):
#     cb.set_param("Simulation_Duration", 2*365)

def draw_from_serialized_file(cb, burnin_dict):
    filepath = os.path.join(burnin_dict["path"], "output")
    cb.set_param("Serialized_Population_Path", filepath)
    cb.set_param("Serialized_Population_Filenames", ["state-18250.dtk"])

    return {"burnin_approx_pfpr2_10": burnin_dict["approximate_pfpr2_10"],
            "burnin_habitat_scale": burnin_dict["habitat_scale"]}

