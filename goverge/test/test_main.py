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

import argparse
import os
import sys

from mock import patch
from mock import Mock
from subprocess import PIPE
from subprocess import Popen
from unittest import TestCase

from goverge import main
from goverge.config import CoverageConfig


class MainTestCase(TestCase):

    @patch('goverge.main.goverge')
    @patch('goverge.main.create_config')
    def test_main(self, mock_config, mock_goverge):
        config = CoverageConfig()
        mock_config.return_value = config
        sys.argv = ["goverge", "--godep"]
        main.main()
        mock_config.assert_called_once_with(argparse.Namespace(covermode='count', go_flags=None, godep=True, html=False, ignore=None, project_import=None, race=False, short=False, tag=None, test_path=None, threads=4, xml=False, xml_dir='/Users/wesleybalvanz/go/src/github.com/Workiva/goverge/xml_reports/'))
        mock_goverge.assert_called_once_with(config)
        self.assertEquals(os.environ.get("GORACE"), "halt_on_error=1")

    @patch('goverge.main.shutil.rmtree')
    def test_delete_folder(self, mock_rmtree):
        main.delete_folder("foo/")
        mock_rmtree.assert_called_once_with("foo/")


@patch('goverge.main.subprocess.Popen')
@patch('goverge.main.generate_coverage')
@patch('goverge.main.os.mkdir')
class GovergeTestCase(TestCase):
    def test_short_race_godep_path_html(
            self, mock_mkdir, gen_cov, mock_popen):
        process_mock = Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        config = CoverageConfig(html=True, project_root="/foo/bar")
        main.goverge(config)

        mock_mkdir.assert_called_once_with("./reports")
        gen_cov.assert_called_once_with(config)
        mock_popen.assert_called_once_with(
            ["go", "tool", "cover", "--html=test_coverage.txt"],
            stdout=PIPE, cwd="/foo/bar")


class parse_argsTestCase(TestCase):
    @patch('goverge.main.os.getcwd', return_value="/foo/bar")
    def test_default(self, mock_getcwd):
        args = main._parse_args([])
        expected = {
            'go_flags': None,
            'covermode': 'count',
            'godep': False,
            'html': False,
            'project_import': None,
            'race': False,
            'short': False,
            'tag': None,
            'test_path': None,
            'threads': 4,
            'xml': False,
            'xml_dir': '/foo/bar/xml_reports/',
            'ignore': None
        }
        self.assertEqual(expected, vars(args))

    def test_custom(self):
        args = main._parse_args([
            '--go_flags=-x',
            '--go_flags=-timeout=5m',
            '--covermode=atomic',
            '--godep',
            "--html",
            "--test_path=/foo/bar",
            "--test_path=/bar/foo",
            "--project_import=github.com/Workiva/goverge",
            "--race",
            '--short',
            "--tag=foo",
            "--threads=12",
            "--xml",
            "--xml_dir=/foo/bar/"
        ])
        expected = {
            'go_flags': ["-x", "-timeout=5m"],
            'covermode': 'atomic',
            'godep': True,
            'html': True,
            'ignore': None,
            'project_import': "github.com/Workiva/goverge",
            'race': True,
            'short': True,
            'tag': "foo",
            'threads': "12",
            'test_path': ['/foo/bar', '/bar/foo'],
            'xml': True,
            'xml_dir': '/foo/bar/',
        }
        self.assertEqual(expected, vars(args))
