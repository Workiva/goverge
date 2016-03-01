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

import glob
import logging
import time


def get_coverage_reports(report_loc):
    """
    Gets all reports in a given location

    :type report_loc: string
    :param report_loc: The location of the reports
    :rtype: list
    :return: A list of reports in the given location
    """

    return [report for report in glob.glob(u"{0}/*.txt".format(report_loc))]


def compile_reports(reports):
    """ Compiles multiple coverage reports into a single report.

    :type reports: list
    :param reports: Reports that will be compiled into a single report.
    """

    # This is dict of [Coverage location] [Coverage report line]
    package_reports = {}

    time_at_beginning = time.clock()
    for report in reports:
        report_start_time = time.clock()
        with open(report) as report_file:
            for line in report_file.readlines():
                # If we get a blank line or a mode line just ignore them
                if line == "mode: count\n" or line == "":
                    continue

                line_parts = line.split(" ")
                if len(line_parts) != 3:
                    logging.error(u"Invalid report line: {}".format(line))
                    continue

                # Check if the line is already in the master list
                master_line = package_reports.get(line_parts[0])
                if master_line:
                    # If the new value is 0 we don't need to update the value
                    if int(line_parts[2]) == 0:
                        continue

                    # Add the line covered count to the master line
                    line_parts[2] = str(
                        int(master_line.split(" ")[2]) +
                        int(line_parts[2])) + "\n"

                    package_reports[line_parts[0]] = " ".join(line_parts)

                # If the line isn't already in the master list just append it
                else:
                    package_reports[line_parts[0]] = line

            print "{0} was processed in: {1} seconds".format(
                report, time.clock() - report_start_time)
    print "Time to process all reports: {0}".format(
        time.clock() - time_at_beginning)
    write_coverage_to_file(package_reports.values())


def write_coverage_to_file(coverage_reports):
    """
    Write the coverage report lines to the coverage file.

    :type coverage_reports: list
    :param coverage_reports: Coverage report lines
    """

    with open("test_coverage.txt", "w") as coverage_file:
        coverage_file.write("mode: set\n")
        coverage_file.write("".join(coverage_reports))
    print "Coverage file created: test_coverage.txt"
