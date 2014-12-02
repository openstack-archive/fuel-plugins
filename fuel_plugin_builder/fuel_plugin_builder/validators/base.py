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
