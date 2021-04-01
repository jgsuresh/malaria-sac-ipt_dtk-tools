
# Run endpoint analyzer on all runs in the suite, and collect ALL results into a single results CSV/dataframe
import sys
import numpy as np
import pandas as pd
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser

from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.Utilities.Experiments import retrieve_experiment


class SaveEndpoint(BaseAnalyzer):
    def __init__(self, save_file=None, output_filename="InsetChart.json"):
        filenames = ['output/{}'.format(output_filename)]
        super().__init__(filenames=filenames)

        self.save_file = save_file

    def combine(self, all_data):
        data_list = []
        for sim in all_data.keys():
            data_list.append(all_data[sim])

        return pd.concat(data_list, ignore_index=True).reset_index(drop=True)

    def finalize(self, all_data):
        sim_data_full = self.combine(all_data)
        if self.save_file:
            sim_data_full.to_csv(self.save_file, index=False)
        return sim_data_full



def get_pfpr2_10_from_summary(data_summary, year_index=0):
    return data_summary['DataByTime']['PfPR_2to10'][year_index]

def get_pfpr_of_custom_agebin_from_summary(data_summary, age_min, age_max, year_index=0):
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])
    pfpr = np.array(data_summary['DataByTimeAndAgeBins']['PfPR by Age Bin'][year_index])

    age_cut = np.logical_and(age_bins > age_min, age_bins <= age_max)
    return np.sum(pop[age_cut]*pfpr[age_cut])/np.sum(pop[age_cut])


def get_annual_incidence_of_custom_agebin_from_summary(data_summary, age_min, age_max, year_index=0):
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])
    incidence = np.array(data_summary['DataByTimeAndAgeBins']['Annual Clinical Incidence by Age Bin'][year_index])

    age_cut = np.logical_and(age_bins > age_min, age_bins <= age_max)
    return np.sum(pop[age_cut]*incidence[age_cut])/np.sum(pop[age_cut])


def get_pop_of_custom_agebin_from_summary(data_summary, age_min, age_max, year_index=0):
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])

    age_cut = np.logical_and(age_bins > age_min, age_bins <= age_max)
    return np.sum(pop[age_cut])



class TransmissionEndpointFromSummary(SaveEndpoint):
    def __init__(self, save_file=None):
        super().__init__(save_file=save_file, output_filename="MalariaSummaryReport_AnnualAverage.json")

    def select_simulation_data(self, data, simulation):
        data_summary = data[self.filenames[0]]

        sim_data = {
            "pfpr0_5": get_pfpr_of_custom_agebin_from_summary(data_summary,0,5,year_index=1),
            "pfpr2_10": get_pfpr_of_custom_agebin_from_summary(data_summary,2,10,year_index=1),
            "pfpr6_15": get_pfpr_of_custom_agebin_from_summary(data_summary,6,15,year_index=1),
            "pfpr15_500": get_pfpr_of_custom_agebin_from_summary(data_summary,15,500,year_index=1),
            "pfpr_all": get_pfpr_of_custom_agebin_from_summary(data_summary,0,500,year_index=1),

            "annual_incidence0_5": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,5,year_index=1),
            "annual_incidence2_10": get_annual_incidence_of_custom_agebin_from_summary(data_summary,2,10,year_index=1),
            "annual_incidence6_15": get_annual_incidence_of_custom_agebin_from_summary(data_summary,6,15,year_index=1),
            "annual_incidence15_500": get_annual_incidence_of_custom_agebin_from_summary(data_summary,15,500,year_index=1),
            "annual_incidence_all": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,500,year_index=1),

            "pop0_5": get_pop_of_custom_agebin_from_summary(data_summary,0,5,year_index=1),
            "pop2_10": get_pop_of_custom_agebin_from_summary(data_summary,2,10,year_index=1),
            "pop6_15": get_pop_of_custom_agebin_from_summary(data_summary,6,15,year_index=1),
            "pop15_500": get_pop_of_custom_agebin_from_summary(data_summary,15,500,year_index=1),
            "pop_all": get_pop_of_custom_agebin_from_summary(data_summary,0,500,year_index=1)
        }


        sim_data["sim_id"] = simulation.id
        for tag in simulation.tags:
            sim_data[tag] = simulation.tags[tag]

        return pd.DataFrame(sim_data, index=[0])


def run_single_analyzer(exp_id, analyzer, savefile_prefix=""):
    SetupParser.default_block = 'HPC'
    SetupParser.init()

    am = AnalyzeManager()
    am.add_analyzer(analyzer())
    exp = retrieve_experiment(exp_id)
    am.add_experiment(exp)
    am.analyze()

    df_return = am.analyzers[0].results
    df_return.to_csv("{}_{}.csv".format(savefile_prefix, exp_id), index=False)
    return df_return

def run_analyzer_for_scenarios(exp_id):
    run_single_analyzer(exp_id, TransmissionEndpointFromSummary, "endpoints")



class SingleYearPfPREndpoint(SaveEndpoint):
    def __init__(self, save_file=None):
        super().__init__(save_file=save_file, output_filename="MalariaSummaryReport_AnnualAverage.json")

    def select_simulation_data(self, data, simulation):
        data_summary = data[self.filenames[0]]

        sim_data = {"pfpr2_10": get_pfpr2_10_from_summary(data_summary)}


        sim_data["sim_id"] = simulation.id
        for tag in simulation.tags:
            sim_data[tag] = simulation.tags[tag]

        return pd.DataFrame(sim_data, index=[0])


def run_analyzer_for_timing_sweep(exp_id):
    run_single_analyzer(exp_id, SingleYearPfPREndpoint, "timing_sweep")



if __name__ == "__main__":
    exp_id = sys.argv[1]
    # run_analyzer_for_scenarios(exp_id)
    run_analyzer_for_timing_sweep(exp_id)
