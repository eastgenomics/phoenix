"""
Runs Phoenix ClinVar annotation resource update
"""

import argparse
import json

from utils.util import is_date_within_n_weeks
from clinvar_file_fetcher import (
    connect_to_website, get_most_recent_clivar_file_info
)


def main(config_path) -> None:
    """Run annotation update for b38 clinvar annotation resource file

    Args:
        config_path (str): Path to config file

    Raises:
        RuntimeError: Most recent clinvar file is over 8 weeks old
    """
    # load config file
    (
        clinvar_base_link, clinvar_link_path, clinvar_weeks_ago
    ) = load_config(config_path)
    ftp = connect_to_website(clinvar_base_link, clinvar_link_path)
    (
        recent_vcf_file, recent_tbi_file, clinvar_version_date,
        recent_vcf_version
    ) = get_most_recent_clivar_file_info(ftp)

    if not is_date_within_n_weeks(clinvar_version_date, clinvar_weeks_ago):
        raise RuntimeError(
            "Most recent clinvar file availble for download is from over"
            + f" {clinvar_weeks_ago} weeks ago"
        )

    print(f"Most recent clinvar annotation resource file: {recent_vcf_file}")
    print(f"Most recent clinvar file index: {recent_tbi_file}")
    print(f"Date of most recent clinvar file version: {clinvar_version_date}")
    print(f"Most recent clinvar file version: {recent_vcf_version}")


def load_config(config_path):
    """Opens config file in json format and reads contents

    Args:
        config_path (str): Path to config file

    Returns:
        clinvar_base_link (str): base ftp link to download clinvar files
        clinvar_link_path (str): link path to download clinvar files
        clinvar_weeks_ago (str): check clinvar file fetched is less than n
            weeks old

    Raises:
        RuntimeError: COnfig file does not contain expected keys
        RuntimeError: Config file key values do not match expected types
    """
    with open(config_path, "r", encoding="utf8") as json_file:
        config = json.load(json_file)
    keys = [
        "CLINVAR_BASE_LINK",
        "CLINVAR_LINK_PATH_B38"
    ]
    if not all(e in config for e in keys):
        raise RuntimeError("Config file does not contain expected keys")
    try:
        clinvar_base_link = config.get("CLINVAR_BASE_LINK")
        clinvar_link_path = config.get("CLINVAR_LINK_PATH_B38")
        clinvar_weeks_ago = int(config.get("CLINVAR_CHECK_NUM_WEEKS_AGO"))
    except (TypeError, ValueError):
        raise RuntimeError(
            "Config file key values do not match expected value types"
        )
    return clinvar_base_link, clinvar_link_path, clinvar_weeks_ago


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--config_file', type=str, required=True)
    # Parse arguments
    args = parser.parse_args()

    main(args.config_file)
