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
from os.path import join as join_path

from fuel_plugin_builder.validators.schemas import v3
from fuel_plugin_builder.validators import ValidatorV2

logger = logging.getLogger(__name__)


class ValidatorV3(ValidatorV2):

    schema = v3.SchemaV3()

    def __init__(self, *args, **kwargs):
        super(ValidatorV3, self).__init__(*args, **kwargs)
        self.network_roles_path = join_path(
            self.plugin_path, 'network_roles.yaml')

    @property
    def basic_version(self):
        return '7.0'

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(
            self.schema.metadata_schema,
            self.meta_path)
        self.check_env_config_attrs()

    def check_network_roles(self):
        self.validate_optional_file_by_schema(
            self.schema.network_roles_schema, self.network_roles_path)

    def check_tasks(self):
        self.validate_optional_file_by_schema(
            self.schema.tasks_schema, self.tasks_path)
