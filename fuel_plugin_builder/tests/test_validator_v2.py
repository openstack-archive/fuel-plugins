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
from fuel_plugin_builder.validators.schemas.v2 import SchemaV2
from fuel_plugin_builder.validators.validator_v2 import ValidatorV2


class TestValidatorV2(BaseValidator):

    __test__ = True
    validator_class = ValidatorV2
    schema_class = SchemaV2

    @mock.patch('fuel_plugin_builder.validators.validator_v2.utils')
    def test_check_tasks(self, utils_mock):
        mocked_methods = [
            'validate_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        utils_mock.parse_yaml.return_value = [
            {'type': 'puppet', 'parameters': 'param1'},
            {'type': 'shell', 'parameters': 'param2'},
            {'type': 'reboot', 'parameters': 'param3'}]

        self.validator.check_tasks()

        self.assertEqual(
            [mock.call('param1', self.schema_class().puppet_parameters,
                       self.validator.tasks_path,
                       value_path=[0, 'parameters']),
             mock.call('param2', self.schema_class().shell_parameters,
                       self.validator.tasks_path,
                       value_path=[1, 'parameters']),
             mock.call('param3', self.schema_class().reboot_parameters,
                       self.validator.tasks_path,
                       value_path=[2, 'parameters'])],
            self.validator.validate_schema.call_args_list)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['6.0', '6.1'],
            'package_version': '2.0.0'}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                'Current plugin format 2.0.0 is not compatible with 6.0 Fuel'
                ' release. Fuel version must be 6.1 or higher.'
                ' Please remove 6.0 version from metadata.yaml file or'
                ' downgrade package_version.'):
            self.validator.check_compatibility()

    @mock.patch('fuel_plugin_builder.validators.validator_v2.utils')
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
