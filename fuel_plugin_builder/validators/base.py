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
    report = None

    @property
    def root_metadata_path(self):
        return self._get_absolute_path(consts.ROOT_FILE_MASK)

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

    def validate(self, plugin_path=None):
        """Entry point of validator.

        :param plugin_path: plugin path that could override init path
        :type plugin_path: str

        :return: report
        :rtype: reports.ReportNode
        """
        # create root reports.ReportNode and place all inspections results
        # under it
        if plugin_path:
            self.plugin_path = plugin_path
        self.report = reports.ReportNode(
            u'Validating plugin at path: {0}'.format(plugin_path)
        )

        self.report.add_nodes(
            checks.path_exists(self.root_metadata_path)
        )

        return self.report

        # if not self.report.is_failed():
        #     try:
        #         root_data = self._load_root_metadata_file()
        #         self.report.add_nodes(
        #             checks.check_fuel_ver_compatible_with_package_ver(
        #                 self.minimal_fuel_version, root_data
        #             )
        #         )
        #
        #     except Exception as exc:
        #         return self.report.error(exc)
        # else:
        #     # nowhere to go, nothing to do, lets shutdown check
        #     return self.report.error(u"Failed to find root metadata file, "
        #                              u"further validation is impossible")
        #
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

    # def check_release_record(self, data):
    #     report = reports.ReportNode(u"Checking release record")
    #
    #     report.add_nodes(
    #         checks.check_multi_json_schema_is_valid(
    #             {
    #                 'puppet': schema_task_v2_1.puppet_task,
    #                 'shell': schema_task_v2_1.shell_task,
    #                 'group': schema_task_v2_1.group_task,
    #                 'skipped': schema_task_v2_1.skipped_task,
    #                 'copy_files': schema_task_v2_1.copy_files_task,
    #                 'sync': schema_task_v2_1.sync_task,
    #                 'upload_file': schema_task_v2_1.upload_file_task,
    #                 'stage': schema_task_v2_1.stage_task,
    #                 'reboot': schema_task_v2_1.reboot_task
    #             }
    #         ),
    #         data
    #     )
    #
    #     return report
