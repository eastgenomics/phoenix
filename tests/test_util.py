import unittest

from bin.utils.util import (
    is_date_within_n_weeks, compare_checksums_md5, get_file_md5,
    download_ftp_file, download_file_upload_DNAnexus,
    upload_file_DNAnexus, check_proj_folder_exists, check_project_exists
)
from unittest.mock import Mock, patch, mock_open
import dxpy
import datetime


class TestUtils(unittest.TestCase):
    def test_is_date_within_n_weeks_pass(self):
        """Test a date 1 week ago is within 4 weeks of today
        """
        date = datetime.date.today() - datetime.timedelta(weeks=1)
        assert is_date_within_n_weeks(date, num_weeks_ago=4)

    def test_is_date_within_n_weeks_fail(self):
        """Test a date 12 weeks ago is not within 4 weeks of today
        """
        date = datetime.date.today() - datetime.timedelta(weeks=12)
        assert not is_date_within_n_weeks(date, num_weeks_ago=4)

    @patch("bin.utils.util.get_file_md5")
    @patch("builtins.open", new_callable=mock_open)
    def test_compare_checksums_md5_pass(self, mocked_open, mock_md5):
        """Test md5 checksum check passes when checksums match
        """
        md5 = "12345678901234567890123456789012"
        mocked_open.read_data = md5
        mock_md5.return_value = md5
        assert compare_checksums_md5("", "")

    @patch("bin.utils.util.get_file_md5")
    @patch("builtins.open", new_callable=mock_open)
    def test_compare_checksums_md5_no_file(self, mocked_open, mock_md5):
        """Test md5 checksum check passes when checksums match
        """
        md5 = "12345678901234567890123456789012"
        mocked_open.side_effect = OSError()
        mock_md5.return_value = md5
        expected_err = (
            "During checksum comparison,"
            + " file  could not be found"
        )
        with self.assertRaisesRegex(RuntimeError, expected_err):
            compare_checksums_md5("", "")

    @patch("bin.utils.util.get_file_md5")
    @patch("builtins.open", new_callable=mock_open)
    def test_compare_checksums_md5_fail(self, mocked_open, mock_md5):
        """Test md5 checksum check fails when checksums do not match
        """
        mock_md5.return_value = "1234567890123456789012345678fail"
        assert not compare_checksums_md5("", "")

    @patch("bin.utils.util.md5")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_file_md5(self, mocked_open, mock_md5):
        """Test md5 checksum can be obtained from file path
        """
        md5 = "12345678901234567890123456789012"
        mocked_open.read_data = md5
        mock_md5.return_value.hexdigest = md5
        assert get_file_md5("") == md5

    @patch("ftplib.FTP.retrbinary")
    @patch("ftplib.FTP.cwd")
    @patch("ftplib.FTP.login")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_ftp_file(
        self, mocked_open, mock_login, mock_cwd, mock_retr
    ):
        """Test ftp file path can be obtained from downloaded file
        """
        download_link_file = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/weekly/file.vcf.gz"
        assert download_ftp_file(download_link_file) == "file.vcf.gz"

    @patch("ftplib.FTP.retrbinary")
    @patch("ftplib.FTP.cwd")
    @patch("ftplib.FTP.login")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_ftp_file_with_name(
        self, mocked_open, mock_login, mock_cwd, mock_retr
    ):
        """Test ftp file path can be obtained from downloaded file
        """
        download_link_file = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/weekly/file.vcf.gz"
        assert download_ftp_file(
            download_link_file, "my_file.vcf.gz"
        ) == "my_file.vcf.gz"

    @patch("bin.utils.util.upload_file_DNAnexus")
    @patch("bin.utils.util.compare_checksums_md5")
    @patch("bin.utils.util.download_ftp_file")
    def test_download_file_upload_DNAnexus_pass(
        self, mock_ftp, mock_md5, mock_upload
    ):
        """Test DNANexus file ID can be returned from ftp file uploaded to
        DNAnexus
        """
        mock_ftp.return_value = ""
        mock_md5.return_value = True
        return_file = "file-1234"
        mock_upload.return_value = return_file
        assert download_file_upload_DNAnexus(
            "", "", "", "", ""
        ) == return_file

    @patch("bin.utils.util.upload_file_DNAnexus")
    @patch("bin.utils.util.compare_checksums_md5")
    @patch("bin.utils.util.download_ftp_file")
    def test_download_file_upload_DNAnexus_fail(
        self, mock_ftp, mock_md5, mock_upload
    ):
        """Test DNANexus file ID is not returned when ftp file checksum does
        not match file
        """
        ftp_name = "my_file.txt"
        mock_ftp.return_value = ftp_name
        mock_md5.return_value = False
        return_file = "file-1234"
        mock_upload.return_value = return_file
        expected_err = (
                f"File {ftp_name} did not match checksum {ftp_name}"
            )
        with self.assertRaisesRegex(RuntimeError, expected_err):
            download_file_upload_DNAnexus(
                "", "", "", "", ""
            )

    @patch("bin.utils.util.dxpy.upload_local_file")
    @patch("bin.utils.util.DXProject.new_folder")
    @patch("bin.utils.util.DXProject")
    @patch("bin.utils.util.check_proj_folder_exists")
    def test_upload_file_DNAnexus(
        self, mock_folder, mock_project, mock_new_folder, mock_upload
    ):
        """Test file ID can be obtained from file uploaded to DNAnexus
        """
        file_id = "file-1234"
        mock_folder.return_value = True
        mock_upload.return_value.get_id.return_value = file_id
        assert upload_file_DNAnexus("", "") == file_id

    @patch("bin.utils.util.dxpy.upload_local_file")
    @patch("bin.utils.util.DXProject.new_folder")
    @patch("bin.utils.util.DXProject")
    @patch("bin.utils.util.check_proj_folder_exists")
    def test_upload_file_DNAnexus_path_exists(
        self, mock_folder, mock_project, mock_new_folder, mock_upload
    ):
        """Test file ID can be obtained from file uploaded to DNAnexus
        when DNAnexus project folder is provided and already exists
        """
        file_id = "file-1234"
        mock_folder.return_value = True
        mock_upload.return_value.get_id.return_value = file_id
        assert upload_file_DNAnexus("", "", "/my_path") == file_id

    @patch("bin.utils.util.dxpy.upload_local_file")
    @patch("bin.utils.util.DXProject.new_folder")
    @patch("bin.utils.util.DXProject")
    @patch("bin.utils.util.check_proj_folder_exists")
    def test_upload_file_DNAnexus_path(
        self, mock_folder, mock_project, mock_new_folder, mock_upload
    ):
        """Test file ID can be obtained from file uploaded to DNAnexus
        when DNAnexus project folder is provided and does not already exist
        """
        file_id = "file-1234"
        mock_folder.return_value = False
        mock_project.return_value.new_folder.return_value = None
        mock_upload.return_value.get_id.return_value = file_id
        assert upload_file_DNAnexus("", "", "/my_path") == file_id

    @patch("bin.utils.util.DXProject")
    def test_check_project_exists(self, mock_proj):
        """Test check_project_exists passes for existing id
        """
        test_proj_id = "project-1234512345"
        assert check_project_exists(test_proj_id)

    @patch("bin.utils.util.DXProject")
    def test_check_project_exists_invalid(self, mock_proj):
        """Test check_project_exists fails for invalid id
        """
        mock_proj.side_effect = dxpy.exceptions.DXError(
            {"error": {"type": "test", "message": "test"}}, ""
        )
        test_proj_id = "project-fail"
        assert not check_project_exists(test_proj_id)

    @patch("bin.utils.util.check_project_exists")
    @patch("bin.utils.util.dxpy.api.project_list_folder")
    def test_check_proj_folder_exists(self, mock_folder, mock_project):
        """Test check_proj_folder_exists passes for existing folder
        """
        mock_project.return_value = True
        test_proj_id = ""
        test_folder = ""
        assert check_proj_folder_exists(test_proj_id, test_folder)

    @patch("bin.utils.util.check_project_exists")
    @patch("dxpy.api.project_list_folder")
    def test_check_proj_folder_exists_invalid_folder(
        self, mock_folder, mock_project
    ):
        """Test check_proj_folder_exists fails for folder not present
        """
        mock_folder.side_effect = (
            Mock(side_effect=dxpy.exceptions.ResourceNotFound(
                {"error": {"type": "test", "message": "test"}}, "")
            )
        )
        test_proj_id = ""
        test_folder = ""
        assert not check_proj_folder_exists(test_proj_id, test_folder)


if __name__ == "__main__":
    unittest.main()
