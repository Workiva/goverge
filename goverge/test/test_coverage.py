from mock import patch
import unittest

from goverge.coverage import generate_package_coverage


@patch('goverge.coverage.get_package_deps')
@patch('goverge.coverage.subprocess')
class TestCoverage(unittest.TestCase):

    def test_generate_package_coverage_godep_short(
            self, mock_subprocess, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]

        generate_package_coverage(
            "test_path", "project_package", "test_package", "project_root",
            True, True)

        mock_deps.assert_called_once_with("project_package", "test_path")

        mock_subprocess.call.assert_called_once_with([
            "godep", "go", "test", '-covermode=set',
            u"-coverprofile=project_root/reports/test_package.txt",
            u"-coverpkg=foo/bar,foo/bar/baz,.", "-short"
        ], cwd="test_path")

    def test_generate_coverage_no_godep_short(
            self, mock_subprocess, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]

        generate_package_coverage(
            "test_path", "project_package", "test_package", "project_root",
            False, False)

        mock_deps.assert_called_once_with("project_package", "test_path")

        mock_subprocess.call.assert_called_once_with([
            "go", "test", '-covermode=set',
            u"-coverprofile=project_root/reports/test_package.txt",
            u"-coverpkg=foo/bar,foo/bar/baz,."
        ], cwd="test_path")
