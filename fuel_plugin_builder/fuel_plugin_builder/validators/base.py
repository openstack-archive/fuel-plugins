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

    def validate_schema(self, data, schema, path):
        logger.debug('Start schema validation for %s file, %s', path, schema)
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as exc:
            value_path = ' -> '.join(map(six.text_type, exc.absolute_path))
            raise errors.ValidationError(
                'Wrong value format "{0}", for file "{1}", {2}'.format(
                    value_path, path, exc.message))

    def validate_file_by_schema(self, schema, path):
        data = utils.parse_yaml(path)
        self.validate_schema(data, schema, path)

    @abc.abstractmethod
    def validate(self):
        """Performs validation
        """
