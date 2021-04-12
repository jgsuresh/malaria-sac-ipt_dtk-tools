
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

def get_annual_incidence_of_custom_agebin_from_summary(data_summary, age_min, age_max, year_index=0, incidence_type="clinical"):
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])

    if incidence_type == "clinical":
        key = 'Annual Clinical Incidence by Age Bin'
    elif incidence_type == "severe":
        key = 'Annual Severe Incidence by Age Bin'
    else:
        raise ValueError

    incidence = np.array(data_summary['DataByTimeAndAgeBins'][key][year_index])

    age_cut = np.logical_and(age_bins > age_min, age_bins <= age_max)
    return np.sum(pop[age_cut]*incidence[age_cut])/np.sum(pop[age_cut])


def get_pop_of_custom_agebin_from_summary(data_summary, age_min, age_max, year_index=0):
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])

    age_cut = np.logical_and(age_bins > age_min, age_bins <= age_max)
    return np.sum(pop[age_cut])


def get_marita_columns_from_summary(data_summary, year_index=0):
    # Get total pop, average age of pop, avg age of clinical and severe cases
    age_bins = np.array(data_summary['Metadata']['Age Bins'])
    pop_by_age_bin = np.array(data_summary['DataByTimeAndAgeBins']['Average Population by Age Bin'][year_index])
    total_pop = np.sum(pop_by_age_bin)
    avg_age = np.sum(age_bins*pop_by_age_bin)/total_pop

    #Note: this may be pretty misleading if any age bins are especially wide
    clinical_incidence_by_age_bin = data_summary['DataByTimeAndAgeBins']['Annual Clinical Incidence by Age Bin'][year_index]
    avg_age_clinical_cases = np.sum(clinical_incidence_by_age_bin*age_bins)/np.sum(clinical_incidence_by_age_bin)

    severe_incidence_by_age_bin = data_summary['DataByTimeAndAgeBins']['Annual Severe Incidence by Age Bin'][year_index]
    avg_age_severe_cases = np.sum(severe_incidence_by_age_bin*age_bins)/np.sum(severe_incidence_by_age_bin)


    return {"avg_age": avg_age,
            "avg_age_clinical_cases": avg_age_clinical_cases,
            "avg_age_severe_cases": avg_age_severe_cases}


class TransmissionEndpointFromSummary(SaveEndpoint):
    def __init__(self, save_file=None, year_index=0):
        super().__init__(save_file=save_file, output_filename="MalariaSummaryReport_AnnualAverage.json")
        self.year_index = year_index

    def select_simulation_data(self, data, simulation):
        data_summary = data[self.filenames[0]]

        sim_data = {
            "pfpr0_5": get_pfpr_of_custom_agebin_from_summary(data_summary,0,6,year_index=self.year_index),
            "pfpr2_10": get_pfpr_of_custom_agebin_from_summary(data_summary,2,11,year_index=self.year_index),
            "pfpr6_15": get_pfpr_of_custom_agebin_from_summary(data_summary,6,16,year_index=self.year_index),
            "pfpr16_500": get_pfpr_of_custom_agebin_from_summary(data_summary,16,500,year_index=self.year_index),
            "pfpr_all": get_pfpr_of_custom_agebin_from_summary(data_summary,0,500,year_index=self.year_index),

            "clinical_incidence0_5": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,6,year_index=self.year_index, incidence_type="clinical"),
            "clinical_incidence2_10": get_annual_incidence_of_custom_agebin_from_summary(data_summary,2,11,year_index=self.year_index, incidence_type="clinical"),
            "clinical_incidence6_15": get_annual_incidence_of_custom_agebin_from_summary(data_summary,6,16,year_index=self.year_index, incidence_type="clinical"),
            "clinical_incidence16_500": get_annual_incidence_of_custom_agebin_from_summary(data_summary,16,500,year_index=self.year_index, incidence_type="clinical"),
            "clinical_incidence_all": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,500,year_index=self.year_index, incidence_type="clinical"),

            "severe_incidence0_5": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,6,year_index=self.year_index, incidence_type="severe"),
            "severe_incidence2_10": get_annual_incidence_of_custom_agebin_from_summary(data_summary,2,11,year_index=self.year_index, incidence_type="severe"),
            "severe_incidence6_15": get_annual_incidence_of_custom_agebin_from_summary(data_summary,6,16,year_index=self.year_index, incidence_type="severe"),
            "severe_incidence16_500": get_annual_incidence_of_custom_agebin_from_summary(data_summary,16,500,year_index=self.year_index, incidence_type="severe"),
            "severe_incidence_all": get_annual_incidence_of_custom_agebin_from_summary(data_summary,0,500,year_index=self.year_index, incidence_type="severe"),

            "pop0_5": get_pop_of_custom_agebin_from_summary(data_summary,0,6,year_index=self.year_index),
            "pop2_10": get_pop_of_custom_agebin_from_summary(data_summary,2,11,year_index=self.year_index),
            "pop6_15": get_pop_of_custom_agebin_from_summary(data_summary,6,16,year_index=self.year_index),
            "pop16_500": get_pop_of_custom_agebin_from_summary(data_summary,16,500,year_index=self.year_index),
            "pop_all": get_pop_of_custom_agebin_from_summary(data_summary,0,500,year_index=self.year_index)
        }

        sim_data.update(get_marita_columns_from_summary(data_summary, year_index=self.year_index))


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


def run_analyzers(exp_id, analyzers, savefile_prefix=""):
    def _remove_duplicate_columns(df):
        columns_to_keep = []
        for c in df.columns:
            if "_duplicated" not in c:
                columns_to_keep.append(c)
        return df[columns_to_keep]


    SetupParser.default_block = 'HPC'
    SetupParser.init()

    am = AnalyzeManager()
    for a in analyzers:
        am.add_analyzer(a())
    exp = retrieve_experiment(exp_id)
    am.add_experiment(exp)
    am.analyze()

    if len(analyzers) == 1:
        df_return = am.analyzers[0].results

    elif len(analyzers) > 1:
        df_list = [x.results for x in am.analyzers]
        df_return = pd.merge(df_list[0], df_list[1],
                             on="sim_id", suffixes=["","_duplicated"])

        # Drop duplicated columns
        # for c in df_result.columns:
        #     if "_duplicated" in c:
        #         df_result.drop(c, inplace=True)
        df_return = _remove_duplicate_columns(df_return)

    else:
        raise ValueError

    df_return.to_csv("{}_{}.csv".format(savefile_prefix, exp_id), index=False)
    return df_return


def run_analyzers_for_scenarios(exp_id):
    run_analyzers(exp_id, [TransmissionEndpointFromSummary, ConsumablesFromCounterReport], "endpoints")



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




class ConsumablesFromCounterReport(SaveEndpoint):
    def __init__(self, save_file=None, output_filename="ReportEventCounter.json"):
        super().__init__(save_file=save_file, output_filename=output_filename)


    def select_simulation_data(self, data, simulation):
        data_summary = data[self.filenames[0]]

        fields_to_get = [
            "Received_Treatment",
            "Received_Test",
            "Received_Campaign_Drugs",
            "Received_RCD_Drugs",
            "Received_SMC",
            "Received_Ivermectin",
            "Received_Primaquine"
        ]

        sim_data = {}

        for f in fields_to_get:
            if f in data_summary["Channels"]:
                sim_data[f] = np.sum(np.array(data_summary["Channels"][f]["Data"]))
            else:
                print("{} field not in counter report.  Skipping...".format(f))

        sim_data["sim_id"] = simulation.id
        for tag in simulation.tags:
            sim_data[tag] = simulation.tags[tag]

        return pd.DataFrame(sim_data, index=[0])


if __name__ == "__main__":
    exp_id = sys.argv[1]
    run_analyzers_for_scenarios(exp_id)
    # run_analyzer_for_timing_sweep(exp_id)
