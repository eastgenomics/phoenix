"""
Handles all functions related to running vep
"""

import dxpy
from utils.util import (
    check_proj_folder_exists, get_most_recent_file_from_version
)


def get_prod_vep_config(ref_proj_id, ref_proj_folder, assay) -> str:
    """gets information on latest production ClinVar file

    Args:
        ref_proj_id (str): DNAnexus project ID for 001 reference project
        ref_proj_folder (str): folder path containing vep config files
        assay (str): name of assay of vep config (TWE, TSO500, MYE)

    Raises:
        RuntimeError: no vep config files could be found in ref project folder
        RuntimeError: project folder does not exist

    Returns:
        id: str
            DNAnexus file ID of vep config file
    """
    if not check_proj_folder_exists(ref_proj_id, ref_proj_folder):
        raise RuntimeError(
            f"Folder {ref_proj_folder} does not exist in project {ref_proj_id}"
        )
    assay = assay.lower()
    name_regex = f"{assay}_vep_config_v*.json"
    config_files = list(dxpy.find_data_objects(
            name=name_regex,
            name_mode='glob',
            project=ref_proj_id,
            folder=ref_proj_folder,
            describe={
                "fields": {
                    "id": True,
                    "name": True,
                    "created": True,
                    "archivalState": True
                }
            }
        ))

    # Error handling if files are not found in 001 reference
    if not config_files:
        raise RuntimeError(
            f"No vep config files matching {name_regex}"
            + " were found in 001 reference project"
        )

    # return the most recent file uploaded found
    if len(config_files) == 1:
        return config_files[0]["id"]
    else:
        return get_most_recent_file_from_version(config_files)
