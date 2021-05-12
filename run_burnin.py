import numpy as np
from dtk.vector.species import set_species_param

from interventions import add_burnin_historical_interventions
from jsuresh_helpers.comps import submit_experiment_to_comps
from jsuresh_helpers.dtk_tools_modfn_sweeps import modfn_sweep_over_seeds
from reports import add_burnin_reports
from setup_sim import build_project_cb, set_ento_splines, burnin_setup


###################
# Run description #
###################
# Run burnins

##################################
# Core malaria config parameters #
##################################
from simtools.ModBuilder import ModFn
from sweeps import modfn_sweep_over_habitat_scale

archetype = "Central"
cb = build_project_cb(archetype=archetype)


##################################
# Run-specific config parameters #
##################################
# e.g. simulation duration, serialization, input files
# cb.set_param("Simulation_Duration", 1*365)
set_ento_splines(cb, habitat_scale=8.9, archetype=archetype)
burnin_setup(cb, archetype)

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
# habitat_scale_array = np.array([8.1,8.2,8.3,8.4,8.6,8.7,8.8,8.9,9.1,9.2,9.3,9.4,9.5,9.6,9.7,9.8,9.9,10])
habitat_scale_array = np.array([8.9])
modlist = modfn_sweep_over_habitat_scale(habitat_scale_array, archetype)
modlists.append(modlist)

num_seeds = 1
modlist = modfn_sweep_over_seeds(num_seeds)
modlists.append(modlist)

def change_adult_lifespan(cb, adult_life_expectacy):
    set_species_param(cb, 'gambiae', "Indoor_Feeding_Fraction", 0.5)
    set_species_param(cb, 'gambiae', 'Adult_Life_Expectancy', adult_life_expectacy)
    set_species_param(cb, 'gambiae', 'Anthropophily', 0.85)
    set_species_param(cb, 'gambiae', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.5)
    set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', adult_life_expectacy)
    set_species_param(cb, 'funestus', 'Anthropophily', 0.65)
    set_species_param(cb, 'funestus', 'Vector_Sugar_Feeding_Frequency', "VECTOR_SUGAR_FEEDING_NONE")

    return {"adult_life_expectancy": adult_life_expectacy}


modlist = [ModFn(change_adult_lifespan, ale) for ale in range(20,50)]
modlists.append(modlist)

####################
# Reports and logs #
####################
add_burnin_reports(cb, include_inset=True)

###############################
# Submission/COMPs parameters #
###############################

comps_experiment_name = "central_lifespan_sweep"
# comps_priority = "Normal"
comps_priority = "Normal"
comps_coreset = "emod_abcd"
# comps_coreset = "emod_32cores"

##################
# Job submission #
##################

if __name__=="__main__":
    submit_experiment_to_comps(cb, comps_experiment_name, comps_priority, comps_coreset, modlists=modlists)


