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

import os
from subprocess import PIPE
from subprocess import Popen


def get_sub_packages(test_path: str, project_root: str, ignore_list: list):
    if test_path:
        return test_path
    return get_test_packages(project_root, ignore_list)


def get_test_packages(project_root: str, ignore_list: list):
    """Get all of the test packages that coverage will be run on."""
    ignores = ["/.", "Godeps", "vendor"]
    if ignore_list is not None:
        ignores.extend(ignore_list)
    directories = []
    for root, subdirs, file_names in os.walk(project_root):
        if not any(subdir in root for subdir in ignores):
            directories.append(root)

    return directories


def get_project_package(project_root: str, project_import: str) -> str:
    """
    Get the project package from either the import passed in or the project
    root using go list

    :return: The project package import path
    """

    if not project_import:
        project_import, _ = Popen(
            ["go", "list"],
            stdout=PIPE,
            cwd=project_root
        ).communicate()
    return project_import.replace("'", "")
