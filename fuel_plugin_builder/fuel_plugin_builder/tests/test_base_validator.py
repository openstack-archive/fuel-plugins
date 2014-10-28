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

import jsonschema
import mock

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.validators import BaseValidator


class TestBaseValidator(BaseTestCase):

    def setUp(self):
        class NewValidator(BaseValidator):
            def validate(self):
                pass

        self.plugin_path = '/tmp/plugin_path'
        self.validator = NewValidator(self.plugin_path)
        self.data = {'data': 'data1'}
        self.schema = {'schema': 'schema1'}

    @mock.patch('fuel_plugin_builder.validators.base.jsonschema')
    def test_validate_schema(self, schema_mock):
        self.validator.validate_schema(
            self.data,
            self.schema,
            'file_path')
        schema_mock.validate.assert_called_once_with(
            self.data,
            self.schema)

    @mock.patch('fuel_plugin_builder.validators.base.jsonschema.validate',
                side_effect=jsonschema.exceptions.ValidationError('p1', 'p2'))
    def test_validate_schema_raises_error(self, validate_mock):
        with self.assertRaisesRegexp(
                errors.ValidationError,
                'Wrong value format "", for file "file_path", p1'):
            self.validator.validate_schema(self.data, self.schema, 'file_path')
        validate_mock.assert_called_once_with(
            self.data,
            self.schema)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    @mock.patch(
        'fuel_plugin_builder.validators.base.BaseValidator.validate_schema')
    def test_validate_file_by_schema(self, validate_mock, utils_mock):
        utils_mock.parse_yaml.return_value = self.data
        self.validator.validate_file_by_schema(self.schema, self.plugin_path)
        utils_mock.parse_yaml.assert_called_once_with(self.plugin_path)
        validate_mock(self.data, self.schema, self.plugin_path)
