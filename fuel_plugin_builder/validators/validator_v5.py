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

# <<<<<<< HEAD
# from os.path import join as join_path
#
# from fuel_plugin_builder.validators.schemas import SchemaV5
# from fuel_plugin_builder.validators import ValidatorV4
#
#
# class ValidatorV5(ValidatorV4):
#
#     schema = SchemaV5()
#
#     def __init__(self, *args, **kwargs):
#         super(ValidatorV5, self).__init__(*args, **kwargs)
#         self.bond_config_path = \
#               join_path(self.plugin_path, 'bond_config.yaml')
#         self.nic_config_path = join_path(self.plugin_path, 'nic_config.yaml')
#         self.node_config_path = \
#               join_path(self.plugin_path, 'node_config.yaml')
#
#     @property
#     def basic_version(self):
#         return '9.0'
#
#     def check_schemas(self):
#         super(ValidatorV5, self).check_schemas()
#         self.check_node_attributes_schema()
#         self.check_interface_attributes_schema(self.bond_config_path)
#         self.check_interface_attributes_schema(self.nic_config_path)
#
#     def check_node_attributes_schema(self):
#         self.validate_file_by_schema(self.schema.node_attributes_schema,
#                                      self.node_config_path,
#                                      allow_not_exists=True)
#
#     def check_interface_attributes_schema(self, file_path):
#         self.validate_file_by_schema(self.schema.node_nic_attributes_schema,
#                                      file_path,
#                                      allow_not_exists=True)
# =======
from fuel_plugin_builder import checks
from fuel_plugin_builder import schemas
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.validator_base import ValidatorBase


class ValidatorV5(ValidatorBase):
    package_version = '5.0.0'

    _tasks_schema = schemas.task_v2_2_0.tasks
    _tasks_types_schemas = {
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
    _node_attributes_schema = schemas.node_attributes_v9_1.node_attributes
    _node_nic_attributes_schema = schemas.node_attributes_v9_1\
        .node_nic_attributes

    def validate(self, data_tree):
        """See ValidatorBase documentation."""
        report = super(ValidatorV5, self).validate(data_tree)
        report.add_nodes(
            checks.json_schema_is_valid(
                schemas.metadata_v9_1.schema,
                data_tree
            )
        )

        report.add_nodes(
            checks.mode_directive(data_tree)
        )

        report.add_nodes(
            checks.legacy_fuel_version(data_tree)
        )

        if data_tree.get('node_attributes_metadata'):
            report.add_nodes(
                checks.json_schema_is_valid(
                    self._node_attributes_schema,
                    data_tree['node_attributes_metadata']
                )
            )
        if data_tree.get('nic_attributes_metadata'):
            report.add_nodes(
                checks.json_schema_is_valid(
                    self._node_nic_attributes_schema,
                    data_tree['nic_attributes_metadata']
                )
            )

        if data_tree.get('bond_attributes_metadata'):
            report.add_nodes(
                checks.json_schema_is_valid(
                    self._node_nic_attributes_schema,
                    data_tree['bond_attributes_metadata']
                )
            )

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
