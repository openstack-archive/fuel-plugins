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

import logging
from os.path import join as join_path

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.schemas import SchemaV3
from fuel_plugin_builder.validators import ValidatorV2

logger = logging.getLogger(__name__)


class ValidatorV3(ValidatorV2):

    schema = SchemaV3()

    def __init__(self, *args, **kwargs):
        super(ValidatorV3, self).__init__(*args, **kwargs)
        self.deployment_tasks_path = join_path(
            self.plugin_path, 'deployment_tasks.yaml')
        self.network_roles_path = join_path(
            self.plugin_path, 'network_roles.yaml')
        self.node_roles_path = join_path(
            self.plugin_path, 'node_roles.yaml')
        self.volumes_path = join_path(
            self.plugin_path, 'volumes.yaml')

    @property
    def basic_version(self):
        return '7.0'

    def validate(self):
        super(ValidatorV3, self).validate()
        self.check_deployment_tasks()

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(
            self.schema.metadata_schema,
            self.meta_path)
        self.validate_file_by_schema(
            self.schema.tasks_schema,
            self.tasks_path,
            allow_not_exists=True
        )
        self.check_env_config_attrs()
        self.check_deployment_tasks_schema()
        self.check_network_roles_schema()
        self.check_node_roles_schema()
        self.check_volumes_schema()

    def check_deployment_tasks_schema(self):
        self.validate_file_by_schema(
            self.schema.deployment_task_schema,
            self.deployment_tasks_path)

    def check_network_roles_schema(self):
        self.validate_file_by_schema(
            self.schema.network_roles_schema,
            self.network_roles_path,
            allow_not_exists=True)

    def check_node_roles_schema(self):
        self.validate_file_by_schema(
            self.schema.node_roles_schema,
            self.node_roles_path,
            allow_not_exists=True)

    def check_volumes_schema(self):
        self.validate_file_by_schema(
            self.schema.volume_schema,
            self.volumes_path,
            allow_not_exists=True)

    def check_deployment_tasks(self):
        logger.debug(
            'Start deployment tasks checking "%s"',
            self.deployment_tasks_path)

        deployment_tasks = utils.parse_yaml(self.deployment_tasks_path)
        schemas = {
            'puppet': self.schema.puppet_task,
            'shell': self.schema.shell_task,
            'group': self.schema.group_task,
            'skipped': self.schema.skipped_task,
            'copy_files': self.schema.copy_files,
            'sync': self.schema.sync,
            'upload_file': self.schema.upload_file,
            'stage': self.schema.stage,
            'reboot': self.schema.reboot}

        for idx, deployment_task in enumerate(deployment_tasks):
            if deployment_task['type'] not in schemas:
                error_msg = 'There is no such task type:' \
                            '{0}'.format(deployment_task['type'])
                raise errors.ValidationError(error_msg)
            self.validate_schema(
                deployment_task,
                schemas[deployment_task['type']],
                self.deployment_tasks_path,
                value_path=[idx])

    def _parse_tasks(self):
        if utils.exists(self.tasks_path):
            tasks = utils.parse_yaml(self.tasks_path)
            # Tasks schema is not checked in check_schemas, thus
            # we perform manual check on parsing tasks file
            if tasks is None:
                raise errors.FileIsEmpty(self.tasks_path)
        return None
