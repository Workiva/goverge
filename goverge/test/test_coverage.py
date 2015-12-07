from mock import patch
from subprocess import Popen
import unittest

from goverge.coverage import generate_package_coverage
from goverge.coverage import get_package_deps


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


class TestPackageDeps(unittest.TestCase):

    @patch('goverge.coverage.subprocess.Popen')
    @patch('goverge.coverage.subprocess.Popen.communicate')
    def test_package_deps(self, mock_communicate, mock_popen):
        mock_popen.return_value = Popen
        mock_communicate.return_value = (
            '[foo/bar/a bar/baz foo/bar/b foo/bar/c]', '')

        deps = get_package_deps("foo/bar", ".")

        mock_communicate.assert_called_once()

        self.assertEquals(deps, ["foo/bar/a", "foo/bar/b", "foo/bar/c", "."])