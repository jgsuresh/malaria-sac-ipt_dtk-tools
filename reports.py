from dtk.utils.reports import add_node_demographics_report
from malaria.reports.MalariaReport import add_event_counter_report, add_summary_report


def add_burnin_reports(cb, include_inset=False):
    add_summary_report(cb, start=45*365)

    if include_inset:
        cb.set_param("Enable_Default_Reporting", 1)
    else:
        cb.set_param("Enable_Default_Reporting", 0)


    events_to_count = [
        "Bednet_Discarded",
        "Bednet_Got_New_One",
        "Bednet_Using",
        "Received_Treatment",
        "Received_SMC"]

    add_event_counter_report(cb,
                             event_trigger_list=events_to_count,
                             duration=365*50)

summary_age_bins = list(range(20)) + list(range(20,125,5))

def add_scenario_reports(cb, include_inset=True, include_bednet_events_in_counter=False):
    add_summary_report(cb, age_bins=summary_age_bins, start=365)

    events_to_count = [
        "Received_Treatment",
        "Received_Test",
        "Received_Campaign_Drugs",
        "Received_RCD_Drugs",
        "Received_SMC",
        "Received_Ivermectin",
        "Received_Primaquine"
    ]
    if include_bednet_events_in_counter:
        events_to_count += ["Bednet_Discarded", "Bednet_Got_New_One", "Bednet_Using"]

    add_event_counter_report(cb,
                             event_trigger_list=events_to_count)

    # drug_events = ["Received_Treatment", "Diagnostic_Survey_0", "Received_Test", "Received_RCD_Drugs",
    #                "Received_Campaign_Drugs"]
    # cb.set_param("Listed_Events", drug_events)
    # cb.set_param("Custom_Individual_Events", drug_events)

    if include_inset:
        cb.set_param("Enable_Default_Reporting", 1)
    else:
        cb.set_param("Enable_Default_Reporting", 0)

def add_testing_reports(cb):
    add_node_demographics_report(cb, IP_key_to_collect='SchoolStatus')
    add_summary_report(cb, ipfilter="SchoolStatus:AttendsSchool", description="AttendsSchool", age_bins=summary_age_bins)
    add_summary_report(cb, ipfilter="SchoolStatus:DoesNotAttendSchool", description="DoesNotAttendSchool", age_bins=summary_age_bins)

    cb.set_param("Report_Detection_Threshold_True_Parasite_Density", 0)
    cb.set_param("Report_Detection_Threshold_PCR_Gametocytes", 0)