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

from fuel_plugin_builder.validators.schemas import SchemaV4
from fuel_plugin_builder.validators import ValidatorV3


class ValidatorV4(ValidatorV3):

    schema = SchemaV4()

    def __init__(self, *args, **kwargs):
        super(ValidatorV4, self).__init__(*args, **kwargs)
        self.components_path = join_path(self.plugin_path, 'components.yaml')

    @property
    def basic_version(self):
        return '8.0'

    def check_metadata_schema(self):
        self.validate_file_by_schema(
            self.schema.metadata_schema,
            self.meta_path,
            check_file_exists=False)

    def check_schemas(self):
        super(ValidatorV4, self).check_schemas()
        self.check_components_schema()

    def check_components_schema(self):
        self.validate_file_by_schema(self.schema.components_schema,
                                     self.components_path,
                                     check_file_exists=False)
