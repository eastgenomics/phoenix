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
    @patch("bin.clinvar_file_fetcher.time.sleep")
    @patch("bin.clinvar_file_fetcher.FTP")
    def test_connect_to_website(self, mock_ftp, mock_sleep):
        assert connect_to_website(
            "https://ftp.ncbi.nlm.nih.gov",
            "/pub/clinvar/vcf_GRCh38/weekly/file.txt"
        ) == mock_ftp.return_value

    @patch("bin.clinvar_file_fetcher.download_file_upload_DNAnexus")
    def test_download_clinvar_dnanexus(self, mock_download):
        """Test that DNAnexus file IDs are returned
        """
        filename = "file-1234"
        mock_download.return_value = filename
        vcf, index = download_clinvar_dnanexus(
            "https://ftp.ncbi.nlm.nih.gov",
            "/pub/clinvar/vcf_GRCh38/weekly/",
            "", "/my_folder", "my_file.vcf.gz", "my_checksum.md5",
            "my_file.vcf.gz.tbi"
        )
        with self.subTest():
            assert vcf == filename
        with self.subTest():
            assert index == filename


if __name__ == "__main__":
    unittest.main()
