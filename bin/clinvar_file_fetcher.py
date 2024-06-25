"""
Get most recent weekly release of ClinVar files
"""

import time
from ftplib import FTP
import re
from ftplib import error_perm


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
    time.sleep(0.1)
    try:
        ftp = FTP(trimmed_link)
        ftp.login()
        ftp.cwd(path)
    except OSError:
        raise RuntimeError("Error: cannot connect to website")
    except error_perm:
        raise RuntimeError(f"Error: cannot find directory {path}")

    return ftp
