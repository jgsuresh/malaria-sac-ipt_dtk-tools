from simtools.Managers.WorkItemManager import WorkItemManager
from simtools.SetupParser import SetupParser
from simtools.AssetManager.FileList import FileList


# Run parameters:
exp_id = "36a1f403-46af-eb11-a2e3-c4346bcb7275"

# ===================================================================================

wi_name = "sac_ipt_analysis_workitem"
command = "python get_endpoints.py {}".format(exp_id)
user_files = FileList(root='ssmt_endpoint', files_in_root=['get_endpoints.py'])

if __name__ == "__main__":
    SetupParser.default_block = 'HPC'
    SetupParser.init()

    wim = WorkItemManager(item_name=wi_name,
                          command=command,
                          user_files=user_files)
    wim.execute(True)
