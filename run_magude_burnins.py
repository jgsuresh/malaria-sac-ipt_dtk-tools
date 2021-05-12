import numpy as np
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_species_param

from interventions import add_burnin_historical_interventions, seasonal_daily_importations, \
    add_burnin_historical_healthseeking
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from reports import add_burnin_reports
from setup_sim import build_project_cb, set_ento_splines, burnin_setup

from simtools.ModBuilder import ModFn
from sweeps import modfn_sweep_over_habitat_scale

###################
# Run description #
###################
# Run burnins

##################################
# Core malaria config parameters #
##################################

archetype = "Magude"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files
# cb.set_param("Simulation_Duration", 1*365)
set_ento_splines(cb, habitat_scale=8.52, archetype=archetype)
# burnin_setup(cb, archetype)

cb.set_param("Simulation_Duration", 50*365)
cb.set_param("Serialization_Type", "TIMESTEP")
cb.set_param("Serialization_Time_Steps", [50 * 365])
cb.set_param("Serialization_Precision", "REDUCED")
add_burnin_historical_healthseeking(cb, archetype)
# NO historical ITNs
seasonal_daily_importations(cb, 25)


#################################################
# Campaign events that apply to ALL simulations #
#################################################
# add_standard_interventions(cb)
# add_burnin_historical_interventions(cb, archetype="Southern")

#####################
# Experiment sweeps #
#####################
modlists = []

# habitat_scale_array = np.round(np.linspace(8,9,11), decimals=1)
# habitat_scale_array = np.array([7.9,8.1,8.3,8.5,8.7,8.9])
# habitat_scale_array = np.array([7.5,7.6,7.7,7.8])
# habitat_scale_array = np.array([7.85,7.9,7.95,8])
# habitat_scale_array = np.array([8.1,8.2,8.3,8.4,8.6,8.7,8.8,8.9,9.1,9.2,9.3,9.4,9.5,9.6,9.7,9.8,9.9,10])
# modlist = modfn_sweep_over_habitat_scale(habitat_scale_array, archetype)
# modlists.append(modlist)

num_seeds = 1
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)


def set_magude_ento_params(cb, old_or_new):
    if old_or_new == "old":
        # set_species(cb, ["arabiensis", "funestus"])

        set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.5)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.9)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    elif old_or_new == "new":
        # set_species(cb, ["arabiensis", "funestus"])

        set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.95)
        set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(cb, 'arabiensis', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

        set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.6)
        set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    else:
        return NotImplementedError

    return {"old_or_new_ento_params": old_or_new}

modlist = [ModFn(set_magude_ento_params, x) for x in ["old", "new"]]
modlists.append(modlist)

modlist = [ModFn(DTKConfigBuilder.set_param, 'x_Temporary_Larval_Habitat', x) for x in [1,5,10]]
modlists.append(modlist)

####################
# Reports and logs #
####################
add_burnin_reports(cb, include_inset=True)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "magude_burnins_ento_comparison_no_historical_ITNs"
# comps_priority = "Normal"
comps_priority = "Normal"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


