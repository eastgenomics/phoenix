import unittest
import sys
import os
sys.path.append(os.path.abspath(
    os.path.join(os.path.realpath(__file__), '../../bin')
))
from bin.clinvar_annotation_update import (
    load_config
)
from unittest.mock import Mock, patch, mock_open


class TestClinvarAnnotationUpdate(unittest.TestCase):
    def test_load_config(self):
        contents = """{
"CLINVAR_BASE_LINK": "https://ftp.ncbi.nlm.nih.gov",
"CLINVAR_LINK_PATH_B38": "/pub/clinvar/vcf_GRCh38/weekly/",
"CLINVAR_CHECK_NUM_WEEKS_AGO": 8,
"UPDATE_PROJECT_ID": "project-xxxx"
}
"""
        with patch("builtins.open", mock_open(read_data=contents)):
            (
                clinvar_base_link, clinvar_link_path, clinvar_weeks_ago,
                update_project_id
            ) = load_config("")
        with self.subTest():
            assert clinvar_base_link == "https://ftp.ncbi.nlm.nih.gov"
        with self.subTest():
            assert clinvar_link_path == "/pub/clinvar/vcf_GRCh38/weekly/"
        with self.subTest():
            assert clinvar_weeks_ago == 8
        with self.subTest():
            assert update_project_id == "project-xxxx"


if __name__ == "__main__":
    unittest.main()
