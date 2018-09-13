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

import io
import mock
import os
import shutil
import unittest

from goverge.reports import compile_reports
from goverge.reports import write_coverage_to_file


class TestCompileReports(unittest.TestCase):
    def setUp(self):
        try:
            shutil.rmtree("reports")
        except OSError:
            pass
        os.mkdir("reports")
        with open("./reports/coverage_foo.txt", "w") as coverage_report:
            coverage_report.write("mode: set\n")
            coverage_report.write("foo/bar/foo.go:2.85,18.2 1 1\n")
            coverage_report.write("foo/bar/foo.go:23.85,25.8 1 0\n")
            coverage_report.write("foo/bar/bar.go:1.85,4.2 1 0\n")
            coverage_report.write("foo/bar/bar.go:7.85,12.8 1 1\n")
            coverage_report.write("")

        with open("./reports/coverage_bar.txt", "w") as coverage_report:
            coverage_report.write("mode: set\n")
            coverage_report.write("foo/bar/foo.go:2.85,18.2 1 1\n")
            coverage_report.write("foo/bar/foo.go:23.85,25.8 1 1\n")
            coverage_report.write("foo/bar/bar.go:1.85,4.2 1 0\n")
            coverage_report.write("foo/bar/bar.go:7.85,12.8 1 0\n")
            coverage_report.write("")

    def tearDown(self):
        os.remove("./reports/coverage_foo.txt")
        os.remove("./reports/coverage_bar.txt")
        os.remove("test_coverage.txt")
        shutil.rmtree("reports")

    def test_compile_reports(self):
        reports = [b"reports/coverage_foo.txt", b"reports/coverage_bar.txt"]

        compile_reports(reports)
        lines = [
            "mode: set\n",
            "foo/bar/foo.go:2.85,18.2 1 2\n",
            "foo/bar/foo.go:23.85,25.8 1 1\n",
            "foo/bar/bar.go:1.85,4.2 1 0\n",
            "foo/bar/bar.go:7.85,12.8 1 1\n"
            ]
        with open("test_coverage.txt", "r") as coverage_file:
            for line in coverage_file.readlines():
                self.assertIn(line, lines)


class TestWriteCoverage(unittest.TestCase):

    def test_write_coverage_to_file(self):
        with mock.patch('goverge.reports.io.open', create=True) as mock_open:
            stream = io.StringIO()
            # patching to make getvalue() work after close() or __exit__()
            stream.close = mock.Mock(return_value=None)
            mock_open.return_value = stream

            coverage_reports = ["foo\n", "bar\n", "baz\n"]

            write_coverage_to_file(coverage_reports)

            mock_open.assert_called_once_with('test_coverage.txt', 'w', encoding='UTF-8')

            contents = stream.getvalue()
            self.assertEquals(contents, 'mode: set\nfoo\nbar\nbaz\n')
