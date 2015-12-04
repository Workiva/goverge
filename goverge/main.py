"""Entry points for goverge."""
import argparse
import os
import shutil
from subprocess import PIPE
from subprocess import Popen
import sys


from coverage import generate_coverage
from reports import compile_reports
from reports import get_coverage_reports


def main():
    """Main entry point into goverge."""
    args = _parse_args(sys.argv[1:])

    goverge(args)


def goverge(options):
    """
    Goverge command-line interface
    :type options: argparse.Namespace
    :param options: Command-line arguments to control Goverge
    """

    try:
        shutil.rmtree('reports')
    except OSError:
        pass

    os.mkdir("./reports")

    project_root = os.getcwd()

    output, _ = Popen(
        ["go", "list", "-f" "'{{.ImportComment}}'"],
        stdout=PIPE,
        cwd=project_root
    ).communicate()

    project_package = output.split("]")[0].split("[")[-1]

    if options.test_path:
        sub_dirs = options.test_path

    else:
        sub_dirs = [x[0] for x in os.walk(project_root)
                    if "/." not in x[0] and "Godeps" not in x[0]]

    generate_coverage(
        sub_dirs, project_package, project_root, options.godep, options.short)

    reports = get_coverage_reports("./reports")

    compile_reports(reports)


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
        '--godep',
        action='store_true',
        default=False,
        help=(
            'Run coverage using the projects godep files.'))
    p.add_argument(
        '--short',
        action='store_true',
        default=False,
        help=(
            'Run coverage using the -short flag'))
    p.add_argument(
        '--test_path',
        default=None,
        action='append',
        help=(
            'Path(s) to a specific package to get the coverage on\n'
            'Example: --test_path path/one --test_path path/two'
        ))

    return p.parse_args(argv)
