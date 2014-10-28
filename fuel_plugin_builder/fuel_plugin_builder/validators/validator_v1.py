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

from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder.validators.schemas import v1

logger = logging.getLogger(__name__)


class ValidatorV1(BaseValidator):

    def __init__(self, *args, **kwargs):
        super(ValidatorV1, self).__init__(*args, **kwargs)
        self.meta_path = join_path(self.plugin_path, 'metadata.yaml')
        self.tasks_path = join_path(self.plugin_path, 'tasks.yaml')

    def validate(self):
        self.check_schemas()
        self.check_tasks()

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(v1.METADATA_SCHEMA, self.meta_path)
        self.validate_file_by_schema(v1.TASKS_SCHEMA, self.tasks_path)

    def check_tasks(self):
        """Json schema doesn't have any conditions, so we have
        to make sure here, that puppet task is really puppet
        and shell task is correct too
        """
        logger.debug('Start tasks checking "%s"', self.tasks_path)
        tasks = utils.parse_yaml(self.tasks_path)

        for task in tasks:
            if task['type'] == 'puppet':
                schema = v1.PUPPET_PARAMETERS
            elif task['type'] == 'shell':
                schema = v1.SHELL_PARAMETERS

            self.validate_schema(task['parameters'], schema, self.tasks_path)
