import glob
import subprocess
import threading


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

    max_threads = 20
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
                short
            ))
            t.daemon = True
            t.start()
            threads.append(t)

        else:
            threads = [thread for thread in threads if thread.is_alive()]


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


def get_package_deps(project_package, test_path):
    """ Gets the packages dependencies that are part of the project.

    :type project_package: string
    :param project_package: The base package of the project
    :type test_path: string
    :param test_path: The path of the package that is under test
    :rtype: list
    :return: Project dependencies
    """
    output, _ = subprocess.Popen(
        ["go", "list", "-f", "'{{.Deps}}'"],
        stdout=subprocess.PIPE, cwd=test_path).communicate()

    package_deps = [
        package.replace("]", "").replace("[", "").replace("'", "")
        for package in output.split()
        if project_package.split("\n")[0] in package]

    package_deps.append(".")

    return package_deps
