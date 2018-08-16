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
import multiprocessing
import os
import subprocess
import sys

from goverge.config import CoverageConfig

_failed = False


def check_failed(return_code):
    """Check if the test run failed and exit with the correct code if it did.
    :type return_code: int
    :param return_code: The return code of a test run
    """
    if return_code != 0:
        global _failed
        _failed = True


def generate_coverage(config: CoverageConfig):
    """ Generate the coverage for a list of packages."""

    jobs = []
    for package in config.sub_packages:

        # If there isn't a test file in the package we skip it.
        if not glob.glob(u"{0}/*_test.go".format(package)):
            continue
        process = multiprocessing.Process(target=generate_package_coverage, args=(
            package,
            package.replace("/", "_").replace(".", ""),
            config
        ))
        process.start()
        jobs.append(process)

    for job in jobs:
        job.join()
    if _failed:
        os._exit(1)


def generate_package_coverage(
        test_path: str,
        test_package: str,
        config: CoverageConfig
):
    """ Generates the coverage report for a package.

    :param test_path: Path that is being tested
    :param test_package: The name of the package under test
    """

    # Get the dependencies of the package we are testing
    package_deps = get_package_deps(config.project_package, config.test_path, config.tag)
    # print(test_package)
    # print(package_deps)
    # print(config.project_root)
    options = [
        u"go", u"test", u'-covermode=' + config.cover_mode,
        u"-coverprofile={0}/reports/{1}.txt".format(
            config.project_root, test_package),
        u"-coverpkg={0}".format(u",".join(package_deps))]

    if config.godep:
        options = ["godep"] + options

    if config.short:
        options.append("-short")

    if config.race:
        options.append("-race")

    if config.tag:
        options.append("-tags={}".format(config.tag))

    if config.go_flags:
        options += config.go_flags

    if config.xml:
        return generate_xml(config.xml_dir + test_package, options, test_path)

    # Generate the coverage report for each of the package dependencies
    p = subprocess.Popen(
        options + ['-v'], cwd=test_path, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    print(p.communicate()[0])
    check_failed(p.returncode)


def generate_xml(output_loc: str, options: list, test_path: str):
    """
    Run tests and generate a xml report

    :param output_loc: The location that the ouput file will be created
    :param options: The command line options to run the tests with
    :param test_path: Path that is being tested
    """

    output_file = output_loc + ".out"

    with open(output_file, "w") as out_file:
        p = subprocess.Popen(
            options + ['-v'], cwd=test_path, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        for line in p.stdout:
            line = line.decode("utf-8")
            sys.stdout.write(line)
            out_file.write(line)
        print(p.communicate()[0])
    subprocess.call([
        "go2xunit", "-input", output_file, "-output",
        output_loc + ".xml"])
    os.remove(output_file)
    check_failed(p.returncode)


def get_package_deps(project_package: str, test_path: str, tag: list):
    """ Gets the packages dependencies that are part of the project.

    :param project_package: The base package of the project
    :param test_path: The path of the package that is under test
    :param tag: A custom build tag to use when running go test
    :return: Project dependencies
    """

    output, _ = subprocess.Popen(
        ["go", "list", "-f", "'{{.Deps}}'",
         "-tags={}".format(tag) if tag else ""],
        stdout=subprocess.PIPE, cwd=test_path).communicate()

    test_output, _ = subprocess.Popen(
        ["go", "list", "-f", "'{{.TestImports}}'",
         "-tags={}".format(tag) if tag else ""],
        stdout=subprocess.PIPE, cwd=test_path).communicate()

    output = test_output.split() + output.split()
    project_path = project_package.split("\n")[0]
    package_deps = []
    for package in list(set(output)):
        package = package.decode("utf-8")
        # Check that the dependency is part of the local project under test and
        # not part of the vendor dependencies
        if "{}/vendor".format(project_path) not in package and project_path in package:
            p = package.replace(u"]", u"").replace(u"[", u"").replace(u"'", u"")
            package_deps.append(p)

    package_deps.append(".")

    return package_deps
