import unittest
import sys
import os
sys.path.append(os.path.abspath(
    os.path.join(os.path.realpath(__file__), '../../bin')
))

from bin.clinvar_file_fetcher import (
    connect_to_website, get_most_recent_clivar_file_info,
    download_clinvar_dnanexus
)
from unittest.mock import Mock, patch, mock_open


class TestClinvarFileFetcher(unittest.TestCase):
    def test_connect_to_website(self):
        pass

    def test_get_most_recent_clivar_file_info(self):
        pass

    def test_download_clinvar_dnanexus(self):
        pass


if __name__ == "__main__":
    unittest.main()
