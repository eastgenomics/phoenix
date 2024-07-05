"""
Utility functions for running Phoenix
"""

import datetime
from hashlib import md5
import wget
import dxpy


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
    # parse checksum from md5 file
    try:
        with open(checksum_path, "rb") as file:
            checksum = file.readline()[0:32]
    except FileNotFoundError:
        raise RuntimeError(
            f"During checksum comparison, file {file_path} could not be found"
        )

    # parse
    md5sum = md5()
    try:
        with open(file_path, "rb") as file:
            data_chunk = file.read(1024)
            while data_chunk:
                md5sum.update(data_chunk)
                data_chunk = file.read(1024)
    except FileNotFoundError:
        raise RuntimeError(
            f"During checksum comparison, checksum file {file_path} could"
            + " not be found"
        )

    checksum = md5sum.hexdigest()
    if checksum == md5sum:
        return True
    else:
        return False


def download_file_upload_DNAnexus(
        download_link_filename, project_id, proj_folder_path,
        download_link_checksum=None
):
    """Download file, compare to checksum (optional), upload to DNAnexus

    Args:
        download_link_filename (str): link to download file
        project_id (str): DNAnexus project ID to upload file to
        proj_folder_path (str): DNAnexus project folder path to upload to
        download_link_checksum (str, optional): link to download checksum for
            file. Defaults to None

    Raises:
        RuntimeError: File did not match checksum
    """
    file = wget.download(download_link_filename)
    # if checksum link is provided, compare to file downloaded
    if download_link_checksum is not None:
        checksum = wget.download(download_link_checksum)
        if not compare_checksums_md5(file, checksum):
            raise RuntimeError(
                f"File {file} did not match checksum {checksum}"
            )

    dxpy.upload_local_file(
        filename=file, project=project_id, folder=proj_folder_path
    )
