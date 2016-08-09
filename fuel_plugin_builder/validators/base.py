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


class BaseValidator(object):
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

    @staticmethod
    def load_root_file(root_file_path=consts.ROOT_FILE_PATH_AND_NAME):
        """Get where is plugin root is located.

        :param root_file_path: where root file is located relative the plugin
        root.
        :type root_file_path: str
        :return:
        """
        try:

            return files_manager.load(root_file_path)
        except IOError:
            raise errors.FileDoesNotExist(
                'No plugin root file found here:\n{}'.format(
                    root_file_path
                ),
            )

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

        result = ReportNode()
        try:
            data = self.load_root_file()
        except Exception as exc:
            result.error(exc.message)

        sys.stdout.write(
            report.render(add_summary=True)
        )

        return report.ok
