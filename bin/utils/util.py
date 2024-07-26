"""
Utility functions for running Phoenix
"""

import datetime
from hashlib import md5
import dxpy
import os
from ftplib import FTP
from urllib.parse import urlparse


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


def get_file_md5(file_path) -> str:
    """Calculate md5 checksum of file

    Args:
        file_path (str): path to file

    Returns:
        str: hex digested md5 checksum of file
    """
    with open(file_path, "rb") as f:
        return md5(f.read()).hexdigest()


def download_ftp_file(download_link_file) -> str:
    """Download file from ftp link

    Args:
        download_link_file (str): ftp download url to file

    Returns:
        str: path to downloaded file
    """
    file = os.path.basename(download_link_file)
    parsed_url_file = urlparse(download_link_file)
    domain = parsed_url_file.netloc
    path = parsed_url_file.path[:-len(file)]
    ftp = FTP(domain)
    ftp.login()
    ftp.cwd(path)
    with open(file, 'wb') as localfile:
        ftp.retrbinary('RETR ' + file, localfile.write, 1024)
    ftp.quit()

    return file


def download_file_upload_DNAnexus(
        download_link_file, project_id, proj_folder_path,
        download_link_checksum=None
) -> str:
    """Download file, compare to checksum (optional), upload to DNAnexus

    Args:
        download_link_file (str): link to download file
        project_id (str): DNAnexus project ID to upload file to
        proj_folder_path (str): DNAnexus project folder path to upload to
        download_link_checksum (str, optional): link to download checksum for
            file. Defaults to None

    Raises:
        RuntimeError: File did not match checksum

    Returns:
        str: DNAnexus file ID for file uploaded
    """
    # download file
    file = download_ftp_file(download_link_file)

    # if checksum link is provided, compare to file downloaded
    if download_link_checksum is not None:
        # download checksum
        checksum = download_ftp_file(download_link_checksum)
        if not compare_checksums_md5(file, checksum):
            raise RuntimeError(
                f"File {file} did not match checksum {checksum}"
            )

    # create new folder, upload files to folder
    project = dxpy.bindings.dxproject.DXProject(dxid=project_id)
    project.new_folder(proj_folder_path, parents=True)
    file_id = dxpy.upload_local_file(
        filename=file, project=project_id, folder=proj_folder_path
    ).get_id()
    return file_id
