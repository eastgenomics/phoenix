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
from ftplib import error_perm


class TestClinvarFileFetcher(unittest.TestCase):
    @patch("bin.clinvar_file_fetcher.time.sleep")
    @patch("bin.clinvar_file_fetcher.FTP")
    def test_connect_to_website(self, mock_ftp, mock_sleep):
        """Test that ftp website can be connected to when a valid link is
        provided
        """
        assert connect_to_website(
            "https://ftp.ncbi.nlm.nih.gov",
            "/pub/clinvar/vcf_GRCh38/weekly/file.txt"
        ) == mock_ftp.return_value

    @patch("bin.clinvar_file_fetcher.time.sleep")
    @patch("bin.clinvar_file_fetcher.FTP")
    def test_connect_to_website_invalid_link(self, mock_ftp, mock_sleep):
        """Test that ftp website connection will fail when invalid link is
        provided
        """
        expected_err = "Error: invalid link provided to connect_to_website"
        with self.assertRaisesRegex(RuntimeError, expected_err):
            connect_to_website(
                "//Invalid_link",
                "/pub/clinvar/vcf_GRCh38/weekly/file.txt"
            )

    @patch("bin.clinvar_file_fetcher.time.sleep")
    @patch("bin.clinvar_file_fetcher.FTP")
    def test_connect_to_website_cannot_connect(self, mock_ftp, mock_sleep):
        """Test that correct error message is returned if ftp website fails to
        connect
        """
        mock_ftp.side_effect = OSError(
            {"error": {"type": "test", "message": "test"}}, ""
        )
        expected_err = "Error: cannot connect to website"
        with self.assertRaisesRegex(RuntimeError, expected_err):
            connect_to_website(
                "https://ftp.ncbi.nlm.nih.gov",
                "/pub/clinvar/vcf_GRCh38/weekly/file.txt"
            )

    @patch("bin.clinvar_file_fetcher.time.sleep")
    @patch("bin.clinvar_file_fetcher.FTP")
    def test_connect_to_website_cannot_find(self, mock_ftp, mock_sleep):
        """Test that ftp website connection will fail when file path cannot be
        found on website and return appropriate error emssage
        """
        mock_ftp.return_value.cwd.side_effect = error_perm(
            {"error": {"type": "test", "message": "test"}}, ""
        )
        path = "/pub/clinvar/vcf_GRCh38/weekly/file.txt"
        expected_err = f"Error: cannot find directory {path}"
        with self.assertRaisesRegex(RuntimeError, expected_err):
            connect_to_website(
                "https://ftp.ncbi.nlm.nih.gov",
                path
            )

    @patch("bin.clinvar_file_fetcher.download_file_upload_DNAnexus")
    def test_download_clinvar_dnanexus(self, mock_download):
        """Test that DNAnexus file IDs are returned when files are downloaded
        from ftp website and uploaded to DNAnexus
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
