"""
Runs Phoenix ClinVar annotation resource update
"""

import argparse
import json
from clinvar_file_fetcher import (
    connect_to_website, get_most_recent_clivar_file_info
)


def run_annotation_update(config_path) -> None:
    """run annotation update for b38 clinvar annotation resource file

    Args:
        config_path (str): path to config file
    """
    # load config file
    clinvar_base_link, clinvar_link_path = load_config(config_path)
    ftp = connect_to_website(clinvar_base_link, clinvar_link_path)
    (
        recent_vcf_file, recent_tbi_file, most_recent_date, recent_vcf_version
    ) = get_most_recent_clivar_file_info(ftp)

    print(f"Most recent clinvar annotation resource file: {recent_vcf_file}")
    print(f"Most recent clinvar file index: {recent_tbi_file}")
    print(f"Date of most recent clinvar file version: {most_recent_date}")
    print(f"Most recent clinvar file version: {recent_vcf_version}")


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
    keys = [
        "CLINVAR_BASE_LINK",
        "CLINVAR_LINK_PATH_B38"
    ]
    if keys not in config:
        raise RuntimeError("Config file does not contain expected keys")
    clinvar_base_link = config.get("CLINVAR_BASE_LINK")
    clinvar_link_path = config.get("CLINVAR_LINK_PATH_B38")
    return clinvar_base_link, clinvar_link_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--config_file', type=str, required=True)
    # Parse arguments
    args = parser.parse_args()

    run_annotation_update(args.config_file)
