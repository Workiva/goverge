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
import os
from subprocess import PIPE
from subprocess import Popen
import sys
from unittest import TestCase

from goverge import main


class MainTestCase(TestCase):

    @patch('goverge.main.goverge')
    def test_main(self, mock_goverge):
        sys.argv = ["goverge", "--godep"]
        main.main()
        mock_goverge.assert_called_once_with(main._parse_args(['--godep']))
        self.assertEquals(os.environ.get("GORACE"), "halt_on_error=1")

    @patch('goverge.main.shutil.rmtree')
    def test_delete_folder(self, mock_rmtree):
        main.delete_folder("foo/")
        mock_rmtree.assert_called_once_with("foo/")

    @patch('goverge.main.Popen')
    @patch('goverge.main.Popen.communicate')
    def test_get_project_package(self, mock_comm, mock_popen):
        mock_popen.return_value = Popen
        mock_comm.return_value = "'foo/bar'", ""
        package = main.get_project_package("/test/foo/bar", "")
        self.assertEquals(package, "foo/bar")


@patch('goverge.main.Popen')
@patch('goverge.main.Popen.communicate')
@patch('goverge.main.generate_coverage')
@patch('goverge.main.os.getcwd', return_value="/foo/bar")
@patch('goverge.main.os.mkdir')
class GovergeTestCase(TestCase):

    def test_short_race_godep_path_html(
            self, mock_mkdir, mock_cwd, gen_cov, mock_comm, mock_popen):

        mock_popen.return_value = Popen
        args = main._parse_args([
            '--godep', '--short', '--race', '--test_path=/foo/bar',
            "--project_import='github.com/Workiva/goverge'", '--html'])
        main.goverge(args)

        mock_mkdir.assert_called_once_with("./reports")
        assert mock_cwd.called
        gen_cov.assert_called_once_with(
            ['/foo/bar'], "github.com/Workiva/goverge", "/foo/bar", True, True,
            False, 'xml_reports/', True, None, False)
        assert mock_comm.called
        mock_popen.assert_called_once_with(
            ["go", "tool", "cover", "--html=test_coverage.txt"],
            stdout=PIPE, cwd="/foo/bar")


class parse_argsTestCase(TestCase):
    def test_godep(self):
        args = main._parse_args(['--godep'])
        expected = {
            'godep': True,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEqual(expected, vars(args))

    def test_html(self):
        args = main._parse_args(["--html"])
        expected = {
            'godep': False,
            'html': True,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))

    def test_integration(self):
        args = main._parse_args(['--integration'])
        expected = {
            'godep': False,
            'html': False,
            'integration': True,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEqual(expected, vars(args))

    def test_short(self):
        args = main._parse_args(['--short'])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': True,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEqual(expected, vars(args))

    def test_tag(self):
        args = main._parse_args(["--tag=foo"])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': "foo",
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))

    def test_path(self):
        args = main._parse_args([
            "--test_path=/foo/bar",
            "--test_path=/bar/foo"
        ])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': ['/foo/bar', '/bar/foo'],
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))

    def test_project_import(self):
        args = main._parse_args([
            "--project_import=github.com/Workiva/goverge"
        ])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': "github.com/Workiva/goverge",
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))

    def test_xml(self):
        args = main._parse_args(["--xml"])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': True,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))

    def test_xml_dir(self):
        args = main._parse_args(["--xml_dir=/foo/bar/"])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": False,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': '/foo/bar/'
        }
        self.assertEquals(expected, vars(args))

    def test_race(self):
        args = main._parse_args(["--race"])
        expected = {
            'godep': False,
            'html': False,
            'integration': False,
            'project_import': None,
            "race": True,
            'short': False,
            'tag': None,
            'test_path': None,
            'xml': False,
            'xml_dir': 'xml_reports/'
        }
        self.assertEquals(expected, vars(args))
