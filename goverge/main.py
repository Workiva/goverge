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

"""Entry points for goverge."""
import argparse
import os
import shutil
from subprocess import PIPE
from subprocess import Popen
import sys

from _pkg_meta import version
from coverage import generate_coverage
from reports import compile_reports
from reports import get_coverage_reports


def delete_folder(folder):
    """Delete a folder using the given path, ignoring OSErrors"""
    try:
        shutil.rmtree(folder)
    except OSError:
        return


def get_project_package(project_root, project_import):
    """
    Get the project package from either the import passed in or the project
    root using go list

    :type project_root: string
    :param project_root: The location of the project root
    :type project_import: string
    :param project_import: The import path for the project root
    :rtype: string
    :return: The project package import path
    """
    if not project_import:

        project_import, _ = Popen(
            ["go", "list"],
            stdout=PIPE,
            cwd=project_root
        ).communicate()
    return project_import.replace("'", "")


def main():
    """Main entry point into goverge."""

    os.environ["GORACE"] = "halt_on_error=1"

    args = _parse_args(sys.argv[1:])

    goverge(args)


def goverge(options):
    """
    Goverge command-line interface
    :type options: argparse.Namespace
    :param options: Command-line arguments to control Goverge
    """

    delete_folder("reports")
    os.mkdir("./reports")

    if options.xml:
        try:
            os.mkdir(options.xml_dir)
        except OSError:
            pass

    project_root = os.getcwd()

    project_package = get_project_package(project_root, options.project_import)

    if options.test_path:
        sub_dirs = options.test_path

    else:
        sub_dirs = [x[0] for x in os.walk(project_root)
                    if "/." not in x[0] and "Godeps" not in x[0]]

    generate_coverage(
        sub_dirs, project_package, project_root, options.godep, options.short,
        options.xml, options.xml_dir, options.race, options.tag,
        int(options.threads), options.go_flags)

    reports = get_coverage_reports("./reports")

    compile_reports(reports)

    if options.html:
        Popen(
            ["go", "tool", "cover", "--html=test_coverage.txt"],
            stdout=PIPE,
            cwd=project_root
        ).communicate()


def _parse_args(argv):
    """
    Parse command-line arguments.

    :type argv: list
    :param argv: Command-line arguments to parse
    :rtype: argparse.Namespace
    :return: Parsed arguments
    """

    p = argparse.ArgumentParser(prog='goverge')

    p.add_argument(
        '--version',
        action='version',
        version='goverge ' + version,
        help='Display the installed version'
    )

    p.add_argument(
        '--go_flags',
        action='append',
        default=None,
        help='Go build flags to use when running tests example: '
             '--go_flags=-x --go_flags=-timeout=10m'
        )

    p.add_argument(
        '--godep',
        action='store_true',
        default=False,
        help='Run coverage using the projects godep files.'
        )

    p.add_argument(
        '--html',
        action='store_true',
        default=False,
        help="View a html report of the coverage file that is generated."
    )

    p.add_argument(
        '--race',
        action='store_true',
        default=False,
        help="Run tests using the -race flag"
    )

    p.add_argument(
        '--project_import',
        action='store',
        help=(
            "The import path of the project. leaving this blank will get the "
            "project name Using go list but in some cases that doesn't work "
            "and needs to be manually entered. "
            "example: github.com/Workiva/goverge"
        )
    )

    p.add_argument(
        '--short',
        action='store_true',
        default=False,
        help='Run coverage using the -short flag'
    )

    p.add_argument(
        '--tag',
        action='store',
        help="Use an optional build tag when running tests."
    )

    p.add_argument(
        '--test_path',
        default=None,
        action='append',
        help=(
            'Path(s) to a specific package to get the coverage on\n'
            'Example: --test_path path/one --test_path path/two'
        )
    )

    p.add_argument(
        '--threads',
        action='store',
        default=4,
        help='The Maximum number of threads to use when running tests.'
    )

    p.add_argument(
        '--xml',
        action='store_true',
        default=False,
        help=(
            "Generate xml reports of test runs, assumes that go2xunit is "
            "installed"
        )
    )

    p.add_argument(
        '--xml_dir',
        action='store',
        default="xml_reports/",
        help="The location to put the xml reports that are generated."
    )

    return p.parse_args(argv)
