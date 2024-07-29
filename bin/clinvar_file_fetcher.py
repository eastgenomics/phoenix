"""
Get most recent weekly release of ClinVar files
"""

from __future__ import annotations
import time
from ftplib import FTP
import re
from ftplib import error_perm
from datetime import datetime

from utils.util import download_file_upload_DNAnexus


def connect_to_website(base_link, path) -> FTP:
    """Generates a FTP object to enable file download from website

    Args:
        base_link (str): Link used to download clivar files
        path (str): Path appended to link in format path/to/dir

    Raises:
        RuntimeError: Invalid link provided to connect_to_website
        RuntimeError: Cannot connect to website
        RuntimeError: Cannot find directory provided as path

    Returns:
        ftplib.FTP: FTP object to enable file download from website
    """

    # remove "https://" from link"
    pattern = r"(http|https)://(.+)"
    result = re.search(pattern, base_link)
    if result is None or len(result.groups()) < 2:
        raise RuntimeError(
            "Error: invalid link provided to connect_to_website"
        )
    else:
        trimmed_link = result.group(2)

    # safety feature to prevent too many requests to server
    time.sleep(0.5)
    try:
        ftp = FTP(trimmed_link)
        ftp.login()
        ftp.cwd(path)
    except OSError:
        raise RuntimeError("Error: cannot connect to website")
    except error_perm:
        raise RuntimeError(f"Error: cannot find directory {path}")

    return ftp


def get_most_recent_clivar_file_info(ftp) -> tuple[
    str, str, datetime.date, str
]:
    """Gets information on most recent clinvar files

    Args:
        ftp (FTP): FTP object to get clinvar files

    Raises:
        RuntimeError: No clinvar vcf files found on ncbi website
        RuntimeError: No clinvar vcf index found on ncbi website

    Returns:
        recent_vcf_file (str): Most recent clinvar vcf filename found
        recent_tbi_file (str): Index file name for most recent vcf found
        most_recent_date (datetime.date): Most recent clinvar file date
        recent_vcf_version (Str): Most recent clinvar version format YYYYMMDD
    """
    # for all file info strings returned by ftp, add names to file_info_list
    file_info_list = []
    file_list = []
    ftp.retrlines('LIST', file_info_list.append)
    clinvar_gz_regex = re.compile(r"^clinvar_[0-9]+\.vcf\.gz$")

    most_recent_date = datetime.strptime("20100101", '%Y%m%d').date()
    clinvar_version = recent_vcf_file = None

    for file_info in file_info_list:
        # if file info is empty, ignore
        if not file_info.strip():
            continue
        # get name portion of file information
        file_name = file_info.split()[-1]
        file_list.append(file_name)

    for file_name in file_list:
        # find most recent version of annotation resource
        if clinvar_gz_regex.match(file_name):
            ftp_vcf = file_name
            ftp_vcf_ver = str(ftp_vcf.split("_")[1].split(".")[0])
            vcf_file_date = datetime.strptime(
                str(ftp_vcf_ver), '%Y%m%d'
            ).date()

            # if current file date is more recent than previous most recent
            # date, set most recent date to current file date
            if most_recent_date < vcf_file_date:
                most_recent_date = vcf_file_date
                clinvar_version = ftp_vcf_ver
                recent_vcf_file = file_name

    if recent_vcf_file is None:
        raise RuntimeError(
            "No ClinVar VCF files could be found on ncbi website"
        )
    # get corresponding .vcf.gz.tbi file based on vcf name
    recent_tbi_file = recent_vcf_file + ".tbi"
    # check index file exists on website
    if recent_tbi_file not in file_list:
        raise RuntimeError(
            "Matching index could not be found for most recent ClinVar VCF"
            + " on ncbi website"
        )

    # get checksum for clinvar file
    clinvar_checksum_file = recent_vcf_file + ".md5"
    # check index file exists on website
    if recent_tbi_file not in file_list:
        raise RuntimeError(
            "Matching checksum could not be found for most recent ClinVar VCF"
            + " on ncbi website"
        )

    return (
        recent_vcf_file, recent_tbi_file, most_recent_date, clinvar_version,
        clinvar_checksum_file
    )


def download_clinvar_dnanexus(
    clinvar_base_link, clinvar_link_path, update_project_id,
    update_folder_name, recent_vcf_file, clinvar_checksum_file,
    recent_tbi_file
) -> tuple[str, str]:
    """Download ClinVar file and index to DNAnexus project

    Args:
        clinvar_base_link (str): Base ftp link to download website
        clinvar_link_path (str): Ftp link path to files to download
        update_project_id (str): DNAnexus project ID for update project
        update_folder_name (str): DNAnexus path to folder used for update
        recent_vcf_file (str): Name of dev clinvar file
        clinvar_checksum_file (str): Name of dev clinvar checksum
        recent_tbi_file (str): Name of dev clinvar index

    Returns:
        dev_clinvar_id (str): DNAnexus file ID for clinvar file
        dev_index_id (str): DNAnexus file ID for clinvar file index
    """
    full_website_link = f"{clinvar_base_link}{clinvar_link_path}"
    vcf_basename = recent_vcf_file.split(".")[0]
    new_vcf_name = f"{vcf_basename}_b38_withchr.vcf.gz"
    dev_clinvar_id = download_file_upload_DNAnexus(
        f"{full_website_link}{recent_vcf_file}",
        update_project_id, update_folder_name, new_vcf_name,
        f"{full_website_link}{clinvar_checksum_file}"
    )
    # the index file does not have a checksum on the ncbi website
    tbi_basename = recent_tbi_file.split(".")[0]
    new_tbi_name = f"{tbi_basename}_b38_withchr.vcf.gz.tbi"
    dev_index_id = download_file_upload_DNAnexus(
        f"{full_website_link}{recent_tbi_file}",
        update_project_id, update_folder_name, new_tbi_name
    )

    return dev_clinvar_id, dev_index_id
