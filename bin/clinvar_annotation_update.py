"""
Runs Phoenix ClinVar annotation resource update
"""

import json
import sys
from clinvar_file_fetcher import connect_to_website


def run_annotation_update(config_path) -> None:
    """run annotation update for b38 clinvar annotation resource file

    Args:
        config_path (str): path to config file
    """
    # load config file
    clinvar_base_link, clinvar_link_path = load_config(config_path)
    ftp = connect_to_website(clinvar_base_link, clinvar_link_path)

    file_list = []
    ftp.retrlines('LIST', file_list.append)
    for file in file_list:
        print(file)
    print("Exiting Phoenix")


def load_config(config_path):
    """opens config file in json format and reads contents

    Args:
        config_path (str): path to config file

    Returns:
        clinvar_base_link (str)
        clinvar_link_path (str)
    """
    with open(config_path, "r", encoding="utf8") as json_file:
        config = json.load(json_file)
    clinvar_base_link = config.get("CLINVAR_BASE_LINK")
    clinvar_link_path = config.get("CLINVAR_LINK_PATH_B38")
    return clinvar_base_link, clinvar_link_path


if __name__ == "__main__":
    # validate arguments
    num_args = len(sys.argv)
    if num_args < 2:
        raise RuntimeError(
            "Error: path to config file must be specified when running"
            + "clinvar_annotation_update.py"
        )

    run_annotation_update(sys.argv[1])
