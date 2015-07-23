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

import mock

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseValidator
from fuel_plugin_builder.validators.schemas.v1 import SchemaV1
from fuel_plugin_builder.validators.validator_v1 import ValidatorV1


class TestValidatorV1(BaseValidator):

    __test__ = True
    validator_class = ValidatorV1
    schema_class = SchemaV1

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
    def test_check_tasks(self, utils_mock):
        mocked_methods = [
            'validate_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        utils_mock.parse_yaml.return_value = [
            {'type': 'puppet', 'parameters': 'param1'},
            {'type': 'shell', 'parameters': 'param2'}]

        self.validator.check_tasks()

        self.assertEqual(
            [mock.call('param1', self.schema_class().puppet_parameters,
                       self.validator.tasks_path,
                       value_path=[0, 'parameters']),
             mock.call('param2', self.schema_class().shell_parameters,
                       self.validator.tasks_path,
                       value_path=[1, 'parameters'])],
            self.validator.validate_schema.call_args_list)

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
    def test_check_tasks_no_parameters_not_failed(self, utils_mock):
        mocked_methods = [
            'validate_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        utils_mock.parse_yaml.return_value = [
            {'type': 'puppet'},
        ]

        self.validator.check_tasks()

        self.assertEqual(
            [mock.call(None, self.schema_class().puppet_parameters,
                       self.validator.tasks_path,
                       value_path=[0, 'parameters'])],
            self.validator.validate_schema.call_args_list)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['5.1', '6.0', '6.1'],
            'package_version': '1.0.0'}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                'Current plugin format 1.0.0 is not compatible with 5.1 Fuel'
                ' release. Fuel version must be 6.0 or higher.'
                ' Please remove 5.1 version from metadata.yaml file or'
                ' downgrade package_version.'):
            self.validator.check_compatibility()
