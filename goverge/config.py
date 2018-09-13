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

import argparse
import os

from typing import Any
from goverge.packages import get_project_package
from goverge.packages import get_sub_packages


class CoverageConfig:
    def __init__(
            self,
            cover_mode: str = None,
            go_flags: list = None,
            godep: bool = None,
            html: bool = None,
            ignore_list: list = None,
            project_import: str = None,
            project_package: str = None,
            project_root: str = None,
            race: bool = None,
            short: bool = None,
            sub_packages: list = None,
            tag: str = None,
            threads: int = 4,
            xml: bool = None,
            xml_dir: str = None,
    ):
        """
        :param cover_mode: The coverage mode to use can be set, count or
        atomic defaults to count
        :param godep: Run coverage using the projects godep files
        :param go_flags: Go build flags to use when running tests example:
        --go_flags=-x --go_flags=-timeout=10m
        :param html: If a html report of the coverage file that is generated
        should be displayed.
        :param ignore_list: List of directories to not run coverage on
        :param project_import: The import path of the project
        :param project_package: The root package of the project
        :param project_root: The root path of the project
        :param race: Run tests using the -race flag
        :param short: Run coverage using the -short flag
        :param sub_packages: Sub packages of the project
        :param tag: Use an optional build tag when running tests.
        :param test_path: Path(s) to a specific package to get the coverage on
        :param xml: If xml reports of test runs should be generated
        :param xml_dir: The location to put the xml reports that are generated
        """
        self.cover_mode = cover_mode
        self.go_flags = go_flags
        self.godep = godep
        self.html = html
        self.ignore_list = ignore_list
        self.project_import = project_import
        self.project_package = project_package
        self.project_root = project_root
        self.race = race
        self.short = short
        self.sub_packages = sub_packages
        self.tag = tag
        self.threads = int(threads)
        self.xml = xml
        self.xml_dir = xml_dir


def create_config(args: argparse.Namespace) -> CoverageConfig:
    project_root = os.getcwd()

    return CoverageConfig(
        cover_mode=args.covermode,
        go_flags=args.go_flags,
        godep=args.godep,
        html=args.html,
        ignore_list=args.ignore,
        project_import=args.project_import,
        project_package=get_project_package(project_root, args.project_import),
        project_root=project_root,
        race=args.race,
        short=args.short,
        sub_packages=get_sub_packages(args.test_path, project_root, args.ignore),
        tag=args.tag,
        threads=args.threads,
        xml=args.xml,
        xml_dir=args.xml_dir
    )
