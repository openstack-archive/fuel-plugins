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

import abc
import logging

import jsonschema
import six

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseValidator(object):

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def validate_schema(self, data, schema, file_path, value_path=None):
        logger.debug(
            'Start schema validation for %s file, %s', file_path, schema)

        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as exc:
            raise errors.ValidationError(
                self._make_error_message(exc, file_path, value_path))

    def _make_error_message(self, exc, file_path, value_path):
        error_msg = "File '{0}', {1}".format(file_path, exc.message)

        if value_path is None:
            value_path = []

        if exc.absolute_path:
            value_path.extend(exc.absolute_path)

        if value_path:
            value_path = ' -> '.join(map(six.text_type, value_path))
            error_msg = '{0}, {1}'.format(
                error_msg, "value path '{0}'".format(value_path))

        return error_msg

    def validate_file_by_schema(self, schema, file_path):
        data = utils.parse_yaml(file_path)
        self.validate_schema(data, schema, file_path)

    @abc.abstractmethod
    def validate(self):
        """Performs validation
        """

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(
            self.schema.metadata_schema(),
            self.meta_path)
        self.validate_file_by_schema(
            self.schema.tasks_schema(),
            self.tasks_path)
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

        self.validate_schema(
            config,
            self.schema.attr_root_schema(),
            self.env_conf_path)

        attrs = config.get('attributes', {})
        for attr_id, attr in six.iteritems(attrs):
            schema = self.schema.attr_element_schema()
            # Metadata object is totally different
            # from the others, we have to set different
            # validator for it
            if attr_id == 'metadata':
                schema = self.schema.attr_meta_schema()

            self.validate_schema(
                attr,
                schema,
                self.env_conf_path,
                value_path=['attributes', attr_id])

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