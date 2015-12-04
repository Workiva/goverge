import os
import unittest

from goverge.reports import write_coverage_to_file


class TestWriteCoverage(unittest.TestCase):
    def setUp(self):
        open("test_coverage.txt", "w").close()

    def tearDown(self):
        os.remove("test_coverage.txt")

    def test_write_coverage_to_file(self):
        coverage_reports = ["foo\n", "bar\n", "baz\n"]

        write_coverage_to_file(coverage_reports)

        with open("test_coverage.txt", "r") as coverage_file:
            self.assertEquals(
                coverage_file.readlines(),
                ['mode: set\n', 'foo\n', 'bar\n', 'baz\n'])


class TestCompileReports(unittest.TestCase):
    def setup(self):
        open("./reports/coverage.txt", "w")