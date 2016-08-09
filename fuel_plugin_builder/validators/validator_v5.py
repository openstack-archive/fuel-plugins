# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

from fuel_plugin_builder import checks
from fuel_plugin_builder.reports import ReportNode
from fuel_plugin_builder import schemas
from fuel_plugin_builder.validators.base import BaseValidator


class ValidatorV5(BaseValidator):
    package_version = '5.0.0'

    def validate(self, data_tree):
        """See BaseValidator documentation."""
        report = ReportNode(u"Data validation:")

        report.add_nodes(
            checks.json_schema_is_valid(
                schemas.metadata_v9_1.metadata,
                data_tree
            )
        )

        report.add_nodes(
            checks.mode_directive(data_tree)
        )

        report.add_nodes(
            checks.legacy_fuel_version(data_tree)
        )

        for release in data_tree.get('releases', []):
            release_report = ReportNode(u'Checking release:')
            for graph_relation in release.get('graphs', []):
                release_report.info(u'Graph: "{}"'.format(
                    graph_relation.get('type'))
                )
                release_report.add_nodes(
                    checks.json_schema_is_valid(
                        schema=schemas.graph_v5_0_0.graph,
                        data=graph_relation
                    )
                )

            report.add_nodes(release_report)
        return report

    @checks.check
    def _check_tasks(self, report, data):
        report.info(u"Checking graph tasks")

        report.add_nodes(
            checks.multi_json_schema_is_valid(
                {
                    'puppet': schemas.task_v2_1.puppet_task,
                    'shell': schemas.task_v2_1.shell_task,
                    'group': schemas.task_v2_1.group_task,
                    'skipped': schemas.task_v2_1.skipped_task,
                    'copy_files': schemas.task_v2_1.copy_files_task,
                    'sync': schemas.task_v2_1.sync_task,
                    'upload_file': schemas.task_v2_1.upload_file_task,
                    'stage': schemas.task_v2_1.stage_task,
                    'reboot': schemas.task_v2_1.reboot_task
                }
            ),
            data
        )

        return report
