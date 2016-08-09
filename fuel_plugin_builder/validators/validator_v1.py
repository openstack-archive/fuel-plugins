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

import checks
from fuel_plugin_builder.validators.base import BaseValidator
import schemas
import utils

logger = logging.getLogger(__name__)


class ValidatorV1(BaseValidator):
    package_version = '1.0.0'

    _tasks_schema = schemas.task_v0_0_2.tasks
    _tasks_types_schemas = {
        'puppet': schemas.task_v0_0_0.puppet_task,
        'shell': schemas.task_v0_0_0.shell_task
    }

    def validate(self, data_tree):
        """See ValidatorBase documentation."""
        report = super(ValidatorV1, self).validate(data_tree)

        metadata_report = utils.ReportNode('metadata')
        metadata_report.add_nodes(
            checks.json_schema_is_valid(
                schemas.metadata_v6_0.schema,
                data_tree
            )
        )
        report.add_nodes(metadata_report)

        report.add_nodes(self._check_tasks(data_tree.get('tasks', [])))

        report.add_nodes(
            checks.env_attributes(
                data_tree.get('environment_config', {}),
                schemas.attributes_v6_1.attr_root,
                schemas.attributes_v6_1.attr_element,
                schemas.attributes_v6_1.attr_meta
            )
        )
        return report

    def _check_tasks(self, tasks_data):
        report = utils.ReportNode('Checking tasks')
        report.add_nodes(
            checks.json_schema_is_valid(
                self._tasks_schema,
                tasks_data
            )
        )
        report.add_nodes(
            checks.multi_json_schema_is_valid(
                self._tasks_types_schemas,
                tasks_data
            )
        )
        return report
