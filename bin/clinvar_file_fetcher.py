"""
Get most recent weekly release of ClinVar files
"""

import time
from ftplib import FTP
import re
from ftplib import error_perm
import datetime


def connect_to_website(base_link, path) -> FTP:
    """generates a FTP object to enable file download from website

    Args:
        base_link (str): link used to download clivar files
        path (str): path appended to link in format path/to/dir

    Raises:
        RuntimeError: invalid link provided to connect_to_website
        RuntimeError: cannot connect to website
        RuntimeError: cannot find directory provided as path

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


def get_most_recent_clivar_file_info(ftp):
    """gets information on most recent clinvar files

    Args:
        ftp (FTP): FTP object to get clinvar files

    Raises:
        RuntimeError: no clinvar vcf files found on ncbi website
        RuntimeError: no clinvar vcf index found on ncbi website

    Returns:
        recent_vcf_file (str): most recent clinvar vcf filename found
        recent_tbi_file (str): index file name for most recent vcf found
        most_recent_date (datetime.datetime): most recent clinvar file date
        recent_vcf_version (Str): most recent clinvar version format YYYYMMDD
    """
    # for all file info strings returned by ftp, add names to file_info_list
    file_info_list = []
    file_list = []
    ftp.retrlines('LIST', file_info_list.append)
    clinvar_gz_regex = re.compile(r"^clinvar_[0-9]+\.vcf\.gz$")

    most_recent_date = datetime.strptime("20100101", '%Y%m%d').date()
    recent_vcf_version = ""
    recent_vcf_file = None

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
                recent_vcf_version = ftp_vcf_ver
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

    return (
        recent_vcf_file, recent_tbi_file, most_recent_date, recent_vcf_version
    )
