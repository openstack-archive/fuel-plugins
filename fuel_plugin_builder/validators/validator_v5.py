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

from os.path import join as join_path

from fuel_plugin_builder.validators.schemas import SchemaV5
from fuel_plugin_builder.validators import ValidatorV4


class ValidatorV5(ValidatorV4):

    schema = SchemaV5()

    def __init__(self, *args, **kwargs):
        super(ValidatorV5, self).__init__(*args, **kwargs)
        self.bond_config_path = join_path(self.plugin_path, 'bond_config.yaml')
        self.nic_config_path = join_path(self.plugin_path, 'nic_config.yaml')
        self.node_config_path = join_path(self.plugin_path, 'node_config.yaml')

    @property
    def basic_version(self):
        return '9.0'

    def check_schemas(self):
        super(ValidatorV5, self).check_schemas()
        self.check_node_attributes_schema()
        self.check_interface_attributes_schema(self.bond_config_path)
        self.check_interface_attributes_schema(self.nic_config_path)

    def check_node_attributes_schema(self):
        self.validate_file_by_schema(self.schema.node_attributes_schema,
                                     self.node_config_path,
                                     allow_not_exists=True)

    def check_interface_attributes_schema(self, file_path):
        self.validate_file_by_schema(self.schema.node_nic_attributes_schema,
                                     file_path,
                                     allow_not_exists=True)
