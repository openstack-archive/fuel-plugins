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
from fuel_plugin_builder.validators.formatchecker import FormatChecker
from fuel_plugin_builder.validators.schemas import SchemaV4
from fuel_plugin_builder.validators import ValidatorV3


logger = logging.getLogger(__name__)


class ValidatorV4(ValidatorV3):

    schema = SchemaV4()

    def __init__(self, *args, **kwargs):
        super(ValidatorV4, self).__init__(format_checker=FormatChecker(
            role_patterns=[self.schema.role_pattern]), *args, **kwargs)
        self.components_path = join_path(self.plugin_path, 'components.yaml')

    @property
    def basic_version(self):
        return '8.0'

    def check_metadata_schema(self):
        self.validate_file_by_schema(
            self.schema.metadata_schema,
            self.meta_path,
            allow_not_exists=True)

    def check_tasks_schema(self):
        self.validate_file_by_schema(
            self.schema.tasks_schema,
            self.tasks_path,
            allow_not_exists=True,
            allow_empty=True
        )

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.check_metadata_schema()
        self.check_tasks_schema()
        self.check_env_config_attrs()
        self.check_deployment_tasks_schema()
        self.check_network_roles_schema()
        self.check_node_roles_schema()
        self.check_volumes_schema()
        self.check_components_schema()

    def check_components_schema(self):
        self.validate_file_by_schema(self.schema.components_schema,
                                     self.components_path,
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
            'copy_files': self.schema.copy_files_task,
            'sync': self.schema.sync_task,
            'upload_file': self.schema.upload_file_task,
            'stage': self.schema.stage_task,
            'reboot': self.schema.reboot_task}

        for idx, deployment_task in enumerate(deployment_tasks):
            if deployment_task['type'] not in schemas:
                error_msg = 'There is no such task type:' \
                            '{0}'.format(deployment_task['type'])
                raise errors.ValidationError(error_msg)
            if deployment_task['type'] not in self.schema.roleless_tasks:
                for role_alias in self.schema.role_aliases:
                    deployment_role = deployment_task.get(role_alias)
                    if deployment_role:
                        break
                else:
                    logger.warn(
                        'Task {0} does not contain {1} fields. That '
                        'may lead to tasks being unassigned to nodes.'.
                        format(deployment_task['id'], '/'.
                               join(self.schema.role_aliases)))

            self.validate_schema(
                deployment_task,
                schemas[deployment_task['type']],
                self.deployment_tasks_path,
                value_path=[idx])

    def check_tasks(self):
        """Check legacy tasks.yaml."""
        logger.debug('Start tasks checking "%s"', self.tasks_path)
        if utils.exists(self.tasks_path):
            # todo(ikutukov): remove self._check_tasks
            tasks = utils.parse_yaml(self.tasks_path)
            if tasks is None:
                return

            schemas = {
                'puppet': self.schema.puppet_parameters,
                'shell': self.schema.shell_parameters,
                'reboot': self.schema.reboot_parameters}

            for idx, task in enumerate(tasks):
                self.validate_schema(
                    task.get('parameters'),
                    schemas[task['type']],
                    self.tasks_path,
                    value_path=[idx, 'parameters'])
        else:
            logger.debug('File "%s" doesn\'t exist', self.tasks_path)
