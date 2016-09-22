# -*- coding: utf-8 -*-

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
from fuel_plugin_builder import schemas
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.validator_base import ValidatorBase


class ValidatorV5(ValidatorBase):
    package_version = '5.0.0'
    minimal_fuel_version = '9.1'

    _data_tree_schemas = {
        '': schemas.metadata_v9_1.schema,
        'tasks': schemas.task_v0_0_2.tasks,
        'deployment_tasks': schemas.task_v2_1_0.tasks,
        'network_roles_metadata': schemas.network_roles_v8_0.schema,
        'node_roles_metadata': schemas.node_roles_v7_0.schema,
        'volumes_metadata': schemas.volumes_v7_0.schema,
        'components_metadata': schemas.components_v8_0.schema,
        'node_attributes_metadata': (
            schemas.node_attributes_v9_1.node_attributes
        ),
        'nic_attributes_metadata': (
            schemas.node_attributes_v9_1.node_nic_attributes
        ),
        'bond_attributes_metadata': (
            schemas.node_attributes_v9_1.node_nic_attributes
        )
    }
    _data_tree_multi_schemas = {
        'tasks': {
            'puppet': schemas.task_v1_0_0.puppet_task,
            'shell': schemas.task_v1_0_0.shell_task,
            'reboot': schemas.task_v1_0_0.reboot_task
        },
        'deployment_tasks': {
            'puppet': schemas.task_v2_1_0.puppet_task,
            'shell': schemas.task_v2_1_0.shell_task,
            'group': schemas.task_v2_1_0.group_task,
            'skipped': schemas.task_v2_1_0.skipped_task,
            'copy_files': schemas.task_v2_1_0.copy_files_task,
            'sync': schemas.task_v2_1_0.sync_task,
            'upload_file': schemas.task_v2_1_0.upload_file_task,
            'stage': schemas.task_v2_1_0.stage_task,
            'reboot': schemas.task_v2_1_0.reboot_task,
            'move_to_bootstrap': schemas.task_v2_2_0.move_to_bootstrap_task,
            'master_shell': schemas.task_v2_2_0.master_shell_task,
            'erase_node': schemas.task_v2_2_0.erase_node_task,
        }
    }

    def validate(self, data_tree):
        """See ValidatorBase documentation."""
        report = super(ValidatorV5, self).validate(data_tree)

        report.add_nodes(
            checks.legacy_fuel_version(data_tree)
        )

        report.add_nodes(
            checks.mode_directive(data_tree)
        )

        # check releases schema
        for release in data_tree.get('releases', []):
            release_report = utils.ReportNode('Checking release:')
            for graph in release.get('graphs', []):
                release_report.info('Graph: "{}"'.format(
                    graph.get('type'))
                )
                release_report.add_nodes(
                    checks.json_schema_is_valid(
                        schema=schemas.graph_v9_1.graph,
                        data=graph
                    )
                )

            report.add_nodes(release_report)
        return report
