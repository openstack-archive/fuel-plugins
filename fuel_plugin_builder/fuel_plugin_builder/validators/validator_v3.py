# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
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

from os.path import join as join_path

from fuel_plugin_builder import utils

from fuel_plugin_builder.validators.schemas.v3 import SchemaV3
from fuel_plugin_builder.validators.validator_v2 import ValidatorV2


class ValidatorV3(ValidatorV2):

    schema = SchemaV3()

    def __init__(self, *args, **kwargs):
        super(ValidatorV3, self).__init__(*args, **kwargs)
        self.deployment_tasks = join_path(
            self.plugin_path, 'deployment_tasks.yaml')
        self.node_roles = join_path(
            self.plugin_path, 'node_roles.yaml')
        self.volumes = join_path(
            self.plugin_path, 'volumes.yaml')
        self.network_roles_path = join_path(
            self.plugin_path, 'network_roles.yaml')

    @property
    def basic_version(self):
        return '7.0'

    def validate(self):
        super(ValidatorV3, self).validate()
        self.check_deployment_tasks()
        self.check_node_roles()
        self.check_volumes()
        self.check_network_roles()

    def check_deployment_tasks(self):
        self.validate_file_by_schema(
            self.schema.deployment_task_schema,
            self.deployment_tasks)

    def check_network_roles(self):
        network_roles = utils.parse_yaml(self.network_roles_path)
        self.validate_schema(
            network_roles, self.schema.network_roles_schema,
            self.network_roles_path)

    def check_node_roles(self):
        self.validate_file_by_schema(
            self.schema.node_role_schema,
            self.node_roles)

    def check_volumes(self):
        self.validate_file_by_schema(
            self.schema.volume_schema,
            self.volumes)
