# -*- coding: utf-8 -*-

#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import logging
import os
import sys
from distutils.version import StrictVersion
from os.path import join as join_path
import jsonschema
import six

from fuel_plugin_builder.validators.files_manager import files_manager
from fuel_plugin_builder import consts
from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.report import ReportNode
from fuel_plugin_builder.validators import checks

logger = logging.getLogger(__name__)


class TestExecutionResult(object):
    def __init__(self, process_handle, out, err):
        self.return_code = process_handle.returncode
        self.stdout = out
        self.stderr = err

    @property
    def has_errors(self):
        return self.return_code != 0

    @property
    def is_return_code_zero(self):
        return self.return_code == 0


class BaseValidator(TestExecutionResult):
    """Base Validator.

    New BaseValidator targeted to plugin package version >= 5.0.0 and using
    Checks to describe custom logic and providing output based on
    ReportNode class.

    Check is a basic logic unit that performing validations with given
    parameters.

    Its not recommended to inherit Validators other than BaseValidator from each
    other creating multiple levels of inheritance because it makes hard to trace,
    test and debug where and what checks is applied.
    """

    package_version = '0.0.0'
    minimal_fuel_version = '0.0'

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def get_absolute_path(self, path='.'):
        """Get absolute path from the relative to the plugins folder.

        :param path: relative path
        :type path: str
        :return: path string
        :rtype: str
        """
        return os.path.join(self.plugin_path, path)

    def load_main_metadata_file(self, main_file_path=consts.ROOT_FILE_MASK):
        """Get plugin root data (usually it's metadata.yaml)

        :param main_file_path: root file is located relative the plugin root
        :type main_file_path: str

        :return: data
        :rtype: list|dict
        """
        try:
            path = self.get_absolute_path(main_file_path)
            return files_manager.load(path)
        except Exception as exc:
            raise exc
            # errors.FileDoesNotExist(
            #     'No plugin root file found here:\n{}'.format(
            #         main_file_path
            #     ),
            # )

    def validate(self, plugin_path=None):
        """Entry point of validator.

        :param plugin_path: plugin path (could override init path)
        :type plugin_path: str

        :return: report
        :rtype: ReportNode
        """
        if plugin_path:
            self.plugin_path = plugin_path

        # create root ReportNode and place all inspections results under it
        report = ReportNode('Validating: {0}'.format(self.plugin_path))

        try:
            root_data = self.load_main_metadata_file()
            report.add_nodes(
                checks.check_release_compatible(
                    self.minimal_fuel_version, root_data
                )
            )

        except Exception as exc:
            report.error(exc)

        return report
