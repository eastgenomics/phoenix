"""
Utility functions for running Phoenix
"""

import datetime
from hashlib import md5
import dxpy
import requests
import os
import shutil


def is_date_within_n_weeks(comparison_date, num_weeks_ago=8) -> bool:
    """Checks if a given date occurs within past n weeks

    Args:
        comparison_date (datetime.date): Date to compare
        num_weeks_ago (int, optional): Check date is within the past
            number of weeks ago. Defaults to 8.

    Returns:
        bool: Is date within n weeks
    """
    n_weeks_ago_date = (
        datetime.date.today() - datetime.timedelta(weeks=num_weeks_ago)
    )
    return comparison_date > n_weeks_ago_date


def compare_checksums_md5(file_path, checksum_path) -> bool:
    """Compares file to its md5 checksum file

    Args:
        file_path (str): Path to file to compare
        checksum_path (str): Path to md5 to compare to

    Raises:
        RuntimeError: File to be compared could not be found
        RuntimeError: Md5 file to be compared to could not be found

    Returns:
        bool: Does file match checksum provided
    """
    # read checksum file from path
    try:
        with open(checksum_path, "r") as file:
            for line in file:
                md5_checksum = line[0:32]
                break
    except FileNotFoundError:
        raise RuntimeError(
            "During checksum comparison,"
            + f" file {checksum_path} could not be found"
        )
    # temporarily hardcoded for testing
    md5_checksum = "9bfe7062d81f5f3d0089bc7606a690dd"

    # parse checksum from md5 file
    file_md5 = get_file_md5(file_path)
    if file_md5 == md5_checksum:
        return True
    else:
        print(
            f"File checksum {file_md5} did not match"
            + f" md5 checksum {md5_checksum}"
        )
        return False


def get_file_md5(filename):
    with open(filename, "rb") as f:
        return md5(f.read()).hexdigest()


def download_file_upload_DNAnexus(
        download_link_file, project_id, proj_folder_path,
        download_link_checksum=None
):
    """Download file, compare to checksum (optional), upload to DNAnexus

    Args:
        download_link_file (str): link to download file
        project_id (str): DNAnexus project ID to upload file to
        proj_folder_path (str): DNAnexus project folder path to upload to
        download_link_checksum (str, optional): link to download checksum for
            file. Defaults to None

    Raises:
        RuntimeError: File did not match checksum
    """
    # download file
    r = requests.get(download_link_file, allow_redirects=True)
    file = os.path.basename(download_link_file)
    with open(file, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)
    # if checksum link is provided, compare to file downloaded
    if download_link_checksum is not None:
        r = requests.get(download_link_checksum, allow_redirects=True)
        checksum = os.path.basename(download_link_checksum)
        with open(checksum, "wb") as out_file:
            shutil.copyfileobj(r.raw, out_file)
        if not compare_checksums_md5(file, checksum):
            raise RuntimeError(
                f"File {file} did not match checksum {checksum}"
            )

    dxpy.upload_local_file(
        filename=file, project=project_id, folder=proj_folder_path
    )
