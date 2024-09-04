"""
Utility functions for running Phoenix
"""

import datetime
from hashlib import md5
import dxpy
import os
from ftplib import FTP
from urllib.parse import urlparse
from dxpy.bindings.dxproject import DXProject
from packaging import version
import re


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

    Returns:
        bool: Does file match checksum provided
    """
    # read checksum file from path
    try:
        with open(checksum_path, "r") as file:
            md5_checksum = file.read()[0:32]
    except OSError:
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
        md5_obj = md5(f.read())
        return md5_obj.hexdigest()


def download_ftp_file(download_link_file, file_name=None) -> str:
    """Download file from ftp link

    Args:
        download_link_file (str): ftp download url to file
        file_name (str, optional): name to upload file as

    Returns:
        str: path to downloaded file
    """
    website_filename = os.path.basename(download_link_file)
    if file_name is None:
        file = website_filename
    else:
        file = file_name
    parsed_url_file = urlparse(download_link_file)
    domain = parsed_url_file.netloc
    path = parsed_url_file.path[:-len(website_filename)]
    ftp = FTP(domain)
    ftp.login()
    ftp.cwd(path)
    with open(file, 'wb') as localfile:
        ftp.retrbinary('RETR ' + website_filename, localfile.write, 1024)
    ftp.quit()

    return file


def download_file_upload_DNAnexus(
        download_link_file, project_id, proj_folder_path, file_name,
        download_link_checksum=None
) -> str:
    """Download file, compare to checksum (optional), upload to DNAnexus

    Args:
        download_link_file (str): link to download file
        project_id (str): DNAnexus project ID to upload file to
        proj_folder_path (str): DNAnexus project folder path to upload to
        file_name (str): name to save file as on DNAnexus
        download_link_checksum (str, optional): link to download checksum for
            file. Defaults to None

    Raises:
        RuntimeError: File did not match checksum

    Returns:
        str: DNAnexus file ID for file uploaded
    """
    # download file
    file = download_ftp_file(download_link_file, file_name)

    # if checksum link is provided, compare to file downloaded
    if download_link_checksum is not None:
        # download checksum
        checksum = download_ftp_file(download_link_checksum)
        if not compare_checksums_md5(file, checksum):
            raise RuntimeError(
                f"File {file} did not match checksum {checksum}"
            )
    file_id = upload_file_DNAnexus(file_name, project_id, proj_folder_path)
    return file_id


def upload_file_DNAnexus(
    file_path, project_id, proj_folder_path=None
) -> str:
    """Uploads local file to DNAnexus and creates folder if needed

    Args:
        file_path (str): path to local file to upload
        project_id (str): DNAnexus project id of project to upload to
        proj_folder_path (str, optional): DNAnexus folder path to upload to

    Returns:
        str: DNAnexus file ID of uploaded file
    """
    # if folder path is None, assume it is created in project root
    # else, create folder if it does not already exist
    if proj_folder_path is not None:
        if not check_proj_folder_exists(project_id, proj_folder_path):
            # create folder
            project = DXProject(dxid=project_id)
            project.new_folder(proj_folder_path, parents=True)

    file_id = dxpy.upload_local_file(
        filename=file_path, project=project_id, folder=proj_folder_path
    ).get_id()
    return file_id


def check_proj_folder_exists(project_id, folder_path) -> bool:
    """Checks if a DNAnexus folder exists in a given project

    Args:
        project_id (str): DNAnexus project ID
        folder_path (str): path to DNAnexus folder

    Raises:
        RuntimeError: project not found

    Returns:
        bool: does folder exist in project
    """
    if not check_project_exists(project_id):
        raise RuntimeError(f"Project {project_id} does not exist")

    try:
        dxpy.api.project_list_folder(
            project_id,
            input_params={"folder": folder_path, "only": "folders"},
            always_retry=True
        )
        return True
    except dxpy.exceptions.ResourceNotFound:
        return False


def check_project_exists(project_id) -> bool:
    """Checks if a DNAnexus project exists from project ID

    Args:
        project_id (str): DNAnexus project ID

    Returns:
        bool: does the specified project exist
    """
    try:
        DXProject(project_id)
        return True
    except dxpy.exceptions.DXError:
        return False


def get_most_recent_file_from_version(files) -> str:
    """get latest file in list by version

    Args:
        file_names (list[list[str]]): results of dxpy.find_data_objects
        to compare

    Raises:
        RuntimeError: all config files have invalid versions

    Returns:
        str: DNAnexus file ID of latest file
    """
    # regex format: v, version number, file extension
    regex = r"v([\.0-9]+?)\.json"
    latest_version = version.parse("0.0.1")
    latest_file = None
    for file in files:
        name = file["describe"]["name"]
        version_str = re.search(regex, name)

        if not version_str:
            # if cannot find match for regex continue
            continue
        try:
            found_version = version_str[1]
            version_parsed = version.parse(found_version)
        except version.InvalidVersion:
            # if version is in invalid format continue
            continue
        if version_parsed > latest_version:
            latest_version = version_parsed
            latest_file = file["id"]

    if latest_file is None:
        raise RuntimeError("All config files have invalid version numbers")
    else:
        return latest_file


def login_DNAnexus(self, dev_proj_id) -> None:
    """logs into DNAnexus

    Raises:
        RuntimeError: DNAnexus user authentification check fails
    """
    DX_SECURITY_CONTEXT = {
        "auth_token_type": "Bearer",
        "auth_token": self.dx_token
    }

    dxpy.set_security_context(DX_SECURITY_CONTEXT)
    # prevent files being accidentally generated outside of dev project
    dxpy.set_workspace_id(dev_proj_id)

    try:
        dxpy.api.system_whoami()
    except Exception:
        raise RuntimeError("DNAnexus user authentification failed")
