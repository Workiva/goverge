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

        with open("./reports/coverage_bar.txt", "w") as coverage_report:
            coverage_report.write("mode: set\n")
            coverage_report.write("foo/bar/foo.go:2.85,18.2 1 0\n")
            coverage_report.write("foo/bar/foo.go:23.85,25.8 1 1\n")
            coverage_report.write("foo/bar/bar.go:1.85,4.2 1 0\n")
            coverage_report.write("foo/bar/bar.go:7.85,12.8 1 0\n")

    def tearDown(self):
        os.remove("./reports/coverage_foo.txt")
        os.remove("./reports/coverage_bar.txt")
        os.remove("test_coverage.txt")
        shutil.rmtree("reports")

    def test_compile_reports(self):
        reports = ["reports/coverage_foo.txt", "reports/coverage_bar.txt"]

        compile_reports(reports)
        lines = [
            "mode: set\n",
            "foo/bar/foo.go:2.85,18.2 1 1\n",
            "foo/bar/foo.go:23.85,25.8 1 1\n",
            "foo/bar/bar.go:1.85,4.2 1 0\n",
            "foo/bar/bar.go:7.85,12.8 1 1\n"
            ]
        with open("test_coverage.txt", "r") as coverage_file:
            for line in coverage_file.readlines():
                self.assertIn(line, lines)


class TestWriteCoverage(unittest.TestCase):

    def tearDown(self):
        os.remove("test_coverage.txt")

    def test_write_coverage_to_file(self):
        coverage_reports = ["foo\n", "bar\n", "baz\n"]

        write_coverage_to_file(coverage_reports)

        with open("test_coverage.txt", "r") as coverage_file:
            self.assertEquals(
                coverage_file.readlines(),
                ['mode: set\n', 'foo\n', 'bar\n', 'baz\n'])
