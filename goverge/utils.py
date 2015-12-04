from subprocess import PIPE
from subprocess import Popen


def get_package_deps(project_package, test_path):
    """ Gets the packages dependencies that are part of the project.

    :type project_package: string
    :param project_package: The base package of the project
    :type test_path: string
    :param test_path: The path of the package that is under test
    :rtype: list
    :return: Project dependencies
    """
    output, _ = Popen(["go", "list", "-f", "'{{.Deps}}'"],
                      stdout=PIPE, cwd=test_path).communicate()

    package_deps = [
        package.split("]")[0].split("[")[-1]
        for package in output.split() if project_package.split("\n")[0] in package]

    package_deps.append(".")

    return package_deps
