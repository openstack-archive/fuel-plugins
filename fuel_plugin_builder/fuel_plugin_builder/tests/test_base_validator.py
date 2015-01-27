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

import mock

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.validators import BaseValidator


class TestBaseValidator(BaseTestCase):

    def setUp(self):
        class NewValidator(BaseValidator):

            @property
            def basic_version(self):
                return None

            def validate(self):
                pass

        self.plugin_path = '/tmp/plugin_path'
        self.validator = NewValidator(self.plugin_path)
        self.data = {'data': 'data1'}
        self.schema = self.make_schema(['data'], {'data': {'type': 'string'}})

    @classmethod
    def make_schema(cls, required, properties):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': required,
            'properties': properties}

    @mock.patch('fuel_plugin_builder.validators.base.jsonschema')
    def test_validate_schema(self, schema_mock):
        self.validator.validate_schema(
            self.data,
            self.schema,
            'file_path')
        schema_mock.validate.assert_called_once_with(
            self.data,
            self.schema)

    def test_validate_schema_raises_error(self):
        schema = self.make_schema(['key'], {'key': {'type': 'string'}})
        data = {}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File 'file_path', 'key' is a required property"):
            self.validator.validate_schema(data, schema, 'file_path')

    def test_validate_schema_raises_error_path_in_message(self):
        schema = self.make_schema(
            ['key'],
            {'key': {'type': 'array', 'items': {'type': 'string'}}})
        data = {'key': ['str', 'str', 0]}

        expected_error = ("File 'file_path', 0 is not of type "
                          "'string', value path 'key -> 2'")
        with self.assertRaisesRegexp(
                errors.ValidationError,
                expected_error):
            self.validator.validate_schema(data, schema, 'file_path')

    def test_validate_schema_raises_error_custom_value_path(self):
        schema = self.make_schema(['key'], {'key': {'type': 'string'}})
        data = {}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File 'file_path', 'key' is a required property, "
                "value path '0 -> path2'"):
            self.validator.validate_schema(
                data, schema, 'file_path', value_path=[0, 'path2'])

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    @mock.patch(
        'fuel_plugin_builder.validators.base.BaseValidator.validate_schema')
    def test_validate_file_by_schema(self, validate_mock, utils_mock):
        utils_mock.parse_yaml.return_value = self.data
        self.validator.validate_file_by_schema(self.schema, self.plugin_path)
        utils_mock.parse_yaml.assert_called_once_with(self.plugin_path)
        validate_mock(self.data, self.schema, self.plugin_path)
