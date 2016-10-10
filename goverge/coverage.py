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
import os
import subprocess
import sys
import threading


def check_failed(return_code):
    """Check if the test run failed and exit with the correct code if it did.
    :type return_code: int
    :param return_code: The return code of a test run
    """
    if return_code != 0:
        os._exit(return_code)


def generate_coverage(
        packages, project_package, project_root, godep, short, xml, xml_dir,
        race, tag, max_threads, go_flags):
    """ Generate the coverage for a list of packages.

    :type package: list
    :param package: Packages to generate coverage for
    :type project_package: string
    :param project_package: The package name of the base of the package
    :type project_root: string
    :param project_root: The project root path
    :type godep: bool
    :param godep: If coverage should run with godep
    :type short: bool
    :param short: If coverage should run with the short flag
    :type xml: bool
    :param xml: If xml test output should be created
    :type xml_dir: string
    :param xml_dir: The location that the xml reports should be made
    :type race: bool
    :param race: If the race flag should be used or not
    :type tag: string
    :param tag: A custom build tag to use when running go test
    :type max_threads: int
    :param max_threads: The maximum number of threads for the tests to run on
    :type go_flags: list
    :param go_flags: list of go build flags to use when running tests
    """

    threads = []
    while threads or packages:

        if len(threads) < max_threads and packages:
            package = packages.pop()

            # If there isn't a test file in the package we skip it.
            if not glob.glob(u"{0}/*_test.go".format(package)):
                continue

            t = threading.Thread(target=generate_package_coverage, args=(
                package,
                project_package,
                package.replace("/", "_").replace(".", ""),
                project_root,
                godep,
                short,
                xml,
                xml_dir,
                race,
                tag,
                go_flags,
            ))
            t.daemon = True
            t.start()
            threads.append(t)

        else:
            threads = [thread for thread in threads if thread.is_alive()]


def generate_package_coverage(
        test_path, project_package, test_package, project_root, godep, short,
        xml, xml_dir, race, tag, go_flags):
    """ Generates the coverage report for a package.

    :type test_path: string
    :param test_path: Path that is being tested
    :type project_package: string
    :param project_package: The package name of the base of the package
    :type test_package: string
    :param test_package: The name of the package under test
    :type project_root: string
    :param project_root: The project root path
    :type godep: bool
    :param godep: If godep should be used when running tests
    :type xml: bool
    :param xml: If xml test output should be created
    :type xml_dir: string
    :param xml_dir: The location that the xml reports should be made
    :type race: bool
    :param race: If the race flag should be used or not
    :type tag: string
    :param tag: A custom build tag to use when running go test
    :type go_flags: list
    :param go_flags: list of go build flags to use when running tests
    """

    # Get the dependencies of the package we are testing
    package_deps = get_package_deps(project_package, test_path, tag)

    options = [
        "go", "test", '-covermode=count',
        u"-coverprofile={0}/reports/{1}.txt".format(
            project_root, test_package),
        u"-coverpkg={0}".format(",".join(package_deps))]

    if godep:
        options = ["godep"] + options

    if short:
        options.append("-short")

    if race:
        options.append("-race")

    if tag:
        options.append("-tags={}".format(tag))

    if go_flags:
        options += go_flags

    if xml:
        return generate_xml(xml_dir + test_package, options, test_path)

    # Generate the coverage report for each of the package dependencies
    check_failed(subprocess.call(options, cwd=test_path))


def generate_xml(output_loc, options, test_path):
    """
    Run tests and generate a xml report

    :type output_loc: string
    :param output_loc: The location that the ouput file will be created
    :type options: list
    :param options: The command line options to run the tests with
    :type test_path: string
    :param test_path: Path that is being tested
    """

    output_file = output_loc + ".out"

    with open(output_file, "w") as out_file:
        p = subprocess.Popen(
            options + ['-v'], cwd=test_path, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        for line in p.stdout:
            sys.stdout.write(line)
            out_file.write(line)
        p.communicate()
    subprocess.call([
        "go2xunit", "-input", output_file, "-output",
        output_loc + ".xml"])
    os.remove(output_file)
    check_failed(p.returncode)


def get_package_deps(project_package, test_path, tag):
    """ Gets the packages dependencies that are part of the project.

    :type project_package: string
    :param project_package: The base package of the project
    :type test_path: string
    :param test_path: The path of the package that is under test
    :type tag: string
    :param tag: A custom build tag to use when running go test
    :rtype: list
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
        # Check that the dependency is part of the local project under test and
        # not part of the vendor dependencies
        if project_path + "/vendor" not in package and project_path in package:
            p = package.replace("]", "").replace("[", "").replace("'", "")
            package_deps.append(p)

    package_deps.append(".")

    return package_deps
