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

import mock
from mock import patch
from subprocess import Popen
import unittest

from goverge.config import CoverageConfig
from goverge import coverage
from goverge.coverage import check_failed
from goverge.coverage import generate_package_coverage
from goverge.coverage import get_package_deps


class TestCheckFailed(unittest.TestCase):
    @patch('goverge.coverage.os._exit')
    def test_check_failed(self, mock_exit):
        check_failed(1)
        print("Failed inside of the test: {}".format(coverage._failed))
        self.assertTrue(coverage._failed)


@patch('goverge.coverage.get_package_deps')
class TestCoverage(unittest.TestCase):

    @patch('goverge.coverage.subprocess.Popen')
    def test_generate_package_coverage_godep_short_race(
            self, mock_subproc_popen, mock_deps):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]
        config = CoverageConfig(
            cover_mode="count",
            project_root="project_root",
            project_package="project_package",
            tag="foo"
        )
        generate_package_coverage("test_path", "test_package", config)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", "foo")

        mock_subproc_popen.assert_called_once_with(
            [
                'go',
                'test',
                '-covermode=count',
                '-coverprofile=project_root/reports/test_package.txt',
                '-coverpkg=foo/bar,foo/bar/baz,.',
                '-tags=foo',
                '-v'
            ],
            cwd='test_path',
            stdout=-1,
            stderr=-1
        )

    @patch('goverge.coverage.subprocess.Popen')
    def test_generate_coverage_no_godep_short_race(self, mock_subproc_popen, mock_deps):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]
        config = CoverageConfig(
            cover_mode="count",
            project_root="project_root",
            project_package="project_package"
        )
        generate_package_coverage("test_path", "test_package", config)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", None)

        mock_subproc_popen.assert_called_once_with(
            [
                'go',
                'test',
                '-covermode=count',
                '-coverprofile=project_root/reports/test_package.txt',
                '-coverpkg=foo/bar,foo/bar/baz,.',
                '-v'
            ],
            cwd='test_path',
            stdout=-1,
            stderr=-1
        )

    @patch('goverge.coverage.generate_xml')
    def test_generate_coverage_xml(self, mock_gen_xml, mock_deps):
        mock_deps.return_value = ["foo/bar", "foo/bar/baz", "."]
        config = CoverageConfig(cover_mode="count",
                                project_root="project_root",
                                xml=True, xml_dir="foo/", project_package="project_package")
        generate_package_coverage(
            "test_path", "test_package", config)

        mock_deps.assert_called_once_with(
            "project_package", "test_path", None)

        mock_gen_xml.assert_called_once_with(
            "foo/test_package",
            [
                "go", "test", '-covermode=count',
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
            b'[foo/bar/a bar/baz foo/bar/b foo/bar/c foo/bar/vendor/baz]', None)

        deps = get_package_deps("foo/bar", ".", [b"foo"])

        mock_communicate.assert_called_once()

        self.assertEquals(
            sorted(deps), sorted(["foo/bar/a", "foo/bar/b", "foo/bar/c", "."]))
