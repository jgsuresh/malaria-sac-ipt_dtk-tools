
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
    SetupParser.default_block = 'HPC'
    SetupParser.init()

    am = AnalyzeManager()
    am.add_analyzer(SingleYearPfPREndpoint())
    exp = retrieve_experiment(exp_id)
    am.add_experiment(exp)
    am.analyze()

    df_return = am.analyzers[0].results
    df_return.to_csv("timing_sweep_{}.csv".format(exp_id), index=False)
    return df_return



if __name__ == "__main__":
    exp_id = sys.argv[1]
    run_analyzer_for_timing_sweep(exp_id)
