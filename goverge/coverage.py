import subprocess
import threading

from utils import get_package_deps


def generate_coverage(packages, project_package, project_root, godep, short):
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
    """

    threads = []
    for package in packages:
        t = threading.Thread(
            target=generate_package_coverage,
            args=(
                package,
                project_package,
                package.replace("/", "_").replace(".", ""),
                project_root,
                godep,
                short
            )
        )
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()


def generate_package_coverage(
        test_path, project_package, test_package, project_root, godep, short):
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
    """

    # Get the dependencies of the package we are testing
    package_deps = get_package_deps(project_package, test_path)

    options = [
        "go", "test", '-covermode=set',
        u"-coverprofile={0}/reports/{1}.txt".format(
            project_root, test_package),
        u"-coverpkg={0}".format(",".join(package_deps))]

    if godep:
        options = ["godep"] + options

    if short:
        options.append("-short")

    # Generate the coverage report for each of the package dependencies

    subprocess.call(options, cwd=test_path)
