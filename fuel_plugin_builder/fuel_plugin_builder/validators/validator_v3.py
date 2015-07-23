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
from os.path import join as join_path

from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.schemas import v3
from fuel_plugin_builder.validators import validator_v2

logger = logging.getLogger(__name__)


class ValidatorV3(validator_v2.ValidatorV2):

    schema = v3.SchemaV3()

    def __init__(self, *args, **kwargs):
        super(ValidatorV3, self).__init__(*args, **kwargs)
        self.network_roles_path = join_path(
            self.plugin_path, 'network_roles.yaml')

    @property
    def basic_version(self):
        return '7.0'

    def validate(self):
        super(ValidatorV3, self).validate()
        self.check_network_roles()

    def check_network_roles(self):
        if not os.path.exists(self.network_roles_path):
            logger.debug('No file "%s". Skipping check.',
                         self.network_roles_path)
            return

        network_roles = utils.parse_yaml(self.network_roles_path)
        self.validate_schema(
            network_roles, self.schema.network_roles_schema,
            self.network_roles_path)
