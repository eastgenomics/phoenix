import unittest

from bin.utils.util import (
    is_date_within_n_weeks, compare_checksums_md5, get_file_md5,
    download_ftp_file, download_file_upload_DNAnexus,
    upload_file_DNAnexus, check_proj_folder_exists, check_project_exists
)
from bin.utils import util
from unittest.mock import Mock, patch, mock_open
import re
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
    def compare_checksums_md5_pass(self, mocked_open, mock_md5):
        md5 = "12345678901234567890123456789012"
        mocked_open.return_value = md5
        mock_md5.return_value = md5
        assert compare_checksums_md5("", "")

    @patch("bin.utils.util.get_file_md5")
    @patch("builtins.open", new_callable=mock_open)
    def compare_checksums_md5_fail(self, mocked_open, mock_md5):
        md5 = "12345678901234567890123456789012"
        mocked_open.return_value = md5
        mock_md5.return_value = "1234567890123456789012345678fail"
        assert not compare_checksums_md5("", "")

    @patch("bin.utils.util.DXProject")
    def test_check_project_exists(self, mock_proj):
        """test check_project_exists passes for existing id
        """
        test_proj_id = "project-1234512345"
        assert check_project_exists(test_proj_id)

    @patch("bin.utils.util.DXProject")
    def test_check_project_exists_invalid(self, mock_proj):
        """test check_project_exists fails for invalid id
        """
        mock_proj.side_effect = dxpy.exceptions.DXError(
            {"error": {"type": "test", "message": "test"}}, ""
        )
        test_proj_id = "project-fail"
        assert not check_project_exists(test_proj_id)

    @patch("bin.utils.util.check_project_exists")
    @patch("bin.utils.util.dxpy.api.project_list_folder")
    def test_check_proj_folder_exists(self, mock_folder, mock_project):
        """test check_proj_folder_exists passes for existing folder
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
        """test check_proj_folder_exists fails for folder not present
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
