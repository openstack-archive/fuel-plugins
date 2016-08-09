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

import logging
import os

from fuel_plugin_builder import files_manager
from fuel_plugin_builder import schemas
from fuel_plugin_builder import consts
from fuel_plugin_builder import reports
from fuel_plugin_builder import checks

logger = logging.getLogger(__name__)


class BaseValidator(object):
    """Base Validator.

    New BaseValidator targeted to plugin package version >= 5.0.0 and using
    Checks to describe custom logic and providing output based on
    reports.ReportNode class.

    Check is a basic logic unit that performing validations with given
    parameters.

    Its not recommended to inherit Validators other than BaseValidator from each
    other creating multiple levels of inheritance because it makes hard to
    trace, test and debug where and what checks is applied.
    """

    package_version = '0.0.1'
    minimal_fuel_version = '0.1'

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def _get_absolute_path(self, path='.'):
        """Get absolute path from the relative to the plugins folder.

        :param path: relative path
        :type path: str

        :return: path string
        :rtype: str
        """
        return os.path.join(self.plugin_path, path)

    def _load_root_metadata_file(self):
        """Get plugin root data (usually, it's metadata.yaml).

        :return: data
        :rtype: list|dict
        """
        return files_manager.files_manager.load(self.root_metadata_path)

    @property
    def root_metadata_path(self):
        """Where is the root plugin data file located."""
        return self._get_absolute_path(consts.ROOT_FILE_MASK)

    def load_data_tree(self, root_path):
        """Loads data from the given plugin path and producing data tree
        that could be validated and used by Fuel business logic.

        :param root_path: plugin root path
        :param root_path: str|basestring

        :return: data tree starting from the data in root metadata file
        :rtype: dict
        """
        return {}

    def validate_data_tree(self, data_tree):
        """Validating data tree starting from plugin root metadata file.

        Validation is supposed to use check function against data tree or its
        separate branches to form validation report composed from the checks
        results.

        :param data_tree: data tree
        :type data_tree: dict

        :return: validation report
        :rtype: reports.ReportNode
        """
        return reports.ReportNode()

    def validate(self, plugin_path=None):
        """Entry point of validator.

        :param plugin_path: plugin path that could override init path
        :type plugin_path: str

        :return: report
        :rtype: reports.ReportNode
        """

        if plugin_path:
            self.plugin_path = plugin_path
        report = reports.ReportNode(
            u"Validating plugin located at: {}".format(self.plugin_path)
        )

        data_tree = self.load_data_tree(self.plugin_path)

        report.info(u"Data loaded, validating data...")

        if report.is_failed():
            report.error(u"Failed to validate root metadata file, further "
                         u"validation is impossible")
        else:
            report.add_nodes(self.validate_data_tree(data_tree))
        return report

        # self.report.add_nodes(
        #     checks.check_with_json_schema(
        #         schemas.schema_task_v2_1_0.deployment_task_schema,
        #         root_data
        #     )
        # )
        # self.report.add_nodes(
        #     reports.ReportNode(u"Checking releases").add_nodes(
        #         map(  # they will return reports.ReportNode instances
        #             checks.check_release_record_v5_0_0,
        #             root_data.get('releases', [])
        #         )
        #     )
        # )

