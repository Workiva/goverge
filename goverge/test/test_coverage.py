"""
Copyright 2016 Workiva, INC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from mock import patch
from subprocess import Popen
import unittest

from goverge.coverage import check_failed
from goverge.coverage import generate_package_coverage
from goverge.coverage import get_package_deps


class TestCheckFailed(unittest.TestCase):

    @patch('goverge.coverage.os._exit')
    def test_check_failed(self, mock_exit):
        check_failed(1)
        mock_exit.assert_called_with(1)


@patch('goverge.coverage.get_package_deps')
class TestCoverage(unittest.TestCase):

    @patch('goverge.coverage.subprocess.call', return_value=0)
    def test_generate_package_coverage_godep_short_race_int(
            self, mock_call, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]

        generate_package_coverage(
            "test_path", "project_package", "test_package", "project_root",
            True, True, False, "foo/", True, "foo", True)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", True)

        mock_call.assert_called_once_with([
            "godep", "go", "test", "-v", '-covermode=set',
            u"-coverprofile=project_root/reports/test_package.txt",
            u"-coverpkg=foo/bar,foo/bar/baz,.", "-short", "-race", "-tag foo"
        ], cwd="test_path")

    @patch('goverge.coverage.subprocess.call', return_value=0)
    def test_generate_coverage_no_godep_short_race(self, mock_call, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]

        generate_package_coverage(
            "test_path", "project_package", "test_package", "project_root",
            False, False, False, "foo/", False, None, False)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", False)

        mock_call.assert_called_once_with([
            "go", "test", "-v", '-covermode=set',
            u"-coverprofile=project_root/reports/test_package.txt",
            u"-coverpkg=foo/bar,foo/bar/baz,."
        ], cwd="test_path")

    @patch('goverge.coverage.generate_xml')
    def test_generate_coverage_xml(self, mock_gen_xml, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]

        generate_package_coverage(
            "test_path", "project_package", "test_package", "project_root",
            False, False, True, "foo/", False, None, False)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", False)

        mock_gen_xml.assert_called_once_with(
            "foo/test_package",
            [
                "go", "test", "-v", '-covermode=set',
                u"-coverprofile=project_root/reports/test_package.txt",
                u"-coverpkg=foo/bar,foo/bar/baz,."
            ],
            "test_path"
        )


class TestPackageDeps(unittest.TestCase):

    @patch('goverge.coverage.subprocess.Popen')
    @patch('goverge.coverage.subprocess.Popen.communicate')
    def test_package_deps(self, mock_communicate, mock_popen):
        mock_popen.return_value = Popen
        mock_communicate.return_value = (
            '[foo/bar/a bar/baz foo/bar/b foo/bar/c]', '')

        deps = get_package_deps("foo/bar", ".", False)

        mock_communicate.assert_called_once()

        self.assertEquals(deps, ["foo/bar/a", "foo/bar/b", "foo/bar/c", "."])

    @patch('goverge.coverage.subprocess.Popen')
    @patch('goverge.coverage.subprocess.Popen.communicate')
    def test_package_deps_int(self, mock_communicate, mock_popen):
        mock_popen.return_value = Popen
        mock_communicate.return_value = (
            'foo/bar/a\nfoo/bar/b\nfoo/tests/c', '')

        deps = get_package_deps("foo/bar", ".", True)

        mock_communicate.assert_called_once()

        self.assertEquals(deps, ["foo/bar/a", "foo/bar/b"])
