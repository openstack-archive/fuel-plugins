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

import six

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder.validators.schemas import v1

logger = logging.getLogger(__name__)


class ValidatorV1(BaseValidator):

    def __init__(self, *args, **kwargs):
        super(ValidatorV1, self).__init__(*args, **kwargs)
        self.meta_path = join_path(self.plugin_path, 'metadata.yaml')
        self.tasks_path = join_path(self.plugin_path, 'tasks.yaml')
        self.env_conf_path = join_path(
            self.plugin_path, 'environment_config.yaml')

    def validate(self):
        self.check_schemas()
        self.check_tasks()
        self.check_releases_paths()

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(v1.METADATA_SCHEMA, self.meta_path)
        self.validate_file_by_schema(v1.TASKS_SCHEMA, self.tasks_path)
        self.check_env_config_attrs()

    def check_env_config_attrs(self):
        """Check attributes in environment config file.

        'attributes' is not required field, but if it's
        present it should contain UI elements OR metadata
        structure.
        """
        config = utils.parse_yaml(self.env_conf_path)
        if not config:
            return

        self.validate_schema(config, v1.ATTR_ROOT_SCHEMA, self.env_conf_path)

        attrs = config.get('attributes', {})
        for attr_id, attr in six.iteritems(attrs):
            schema = v1.ATTR_ELEMENT_SCHEMA
            # Metadata object is totally different
            # from the others, we have to set different
            # validator for it
            if attr_id == 'metadata':
                schema = v1.ATTR_META_SCHEMA

            self.validate_schema(
                attr,
                schema,
                self.env_conf_path,
                value_path=['attributes', attr_id])

    def check_tasks(self):
        """Json schema doesn't have any conditions, so we have
        to make sure here, that puppet task is really puppet
        and shell task is correct too
        """
        logger.debug('Start tasks checking "%s"', self.tasks_path)
        tasks = utils.parse_yaml(self.tasks_path)

        schemas = {
            'puppet': v1.PUPPET_PARAMETERS,
            'shell': v1.SHELL_PARAMETERS}

        for idx, task in enumerate(tasks):
            self.validate_schema(
                task['parameters'],
                schemas[task['type']],
                self.tasks_path,
                value_path=[idx, 'parameters'])

    def check_releases_paths(self):
        meta = utils.parse_yaml(self.meta_path)
        for release in meta['releases']:
            scripts_path = join_path(
                self.plugin_path,
                release['deployment_scripts_path'])
            repo_path = join_path(
                self.plugin_path,
                release['repository_path'])

            wrong_paths = []
            for path in [scripts_path, repo_path]:
                if not utils.exists(path):
                    wrong_paths.append(path)

            if wrong_paths:
                raise errors.ReleasesDirectoriesError(
                    'Cannot find directories {0} for release "{1}"'.format(
                        ', '.join(wrong_paths), release))
