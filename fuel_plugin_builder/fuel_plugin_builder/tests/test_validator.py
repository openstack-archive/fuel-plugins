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
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.validators import ValidatorV1
from fuel_plugin_builder.validators import ValidatorV2

from fuel_plugin_builder.validators.schemas.v1 import SchemaV1
from fuel_plugin_builder.validators.schemas.v2 import SchemaV2


@mock.patch('fuel_plugin_builder.validators.base.utils')
class BaseValidator(BaseTestCase):

    __test__ = False
    validator_class = None
    schema_class = None

    def setUp(self):
        self.plugin_path = '/tmp/plugin_path'
        self.validator = self.validator_class(self.plugin_path)

    def test_validate(self, _):
        mocked_methods = [
            'check_schemas',
            'check_tasks',
            'check_releases_paths',
            'check_compatibility',
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.validator.validate()

        self.validator.check_tasks.assert_called_once_with()
        self.validator.check_schemas.assert_called_once_with()
        self.validator.check_releases_paths.assert_called_once_with()
        self.validator.check_compatibility.assert_called_once_with()

    def test_check_schemas(self, _):
        mocked_methods = [
            'check_env_config_attrs',
            'validate_file_by_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(
                self.schema_class().metadata_schema,
                self.validator.meta_path),
             mock.call(
                 self.schema_class().tasks_schema,
                 self.validator.tasks_path)],
            self.validator.validate_file_by_schema.call_args_list)
        self.validator.check_env_config_attrs.assert_called_once_with()

    def test_check_releases_paths(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': '/tmp/repository_path'}]}

        utils_mock.exists.return_value = True
        self.validator.check_releases_paths()
        self.assertEqual(
            utils_mock.exists.call_args_list,
            [mock.call('/tmp/deployment_scripts_path'),
             mock.call('/tmp/repository_path')])

    def test_check_releases_paths_error(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': '/tmp/repository_path'}]}

        utils_mock.exists.return_value = False
        with self.assertRaisesRegexp(
                errors.ReleasesDirectoriesError,
                'Cannot find directories /tmp/deployment_scripts_path'
                ', /tmp/repository_path for release '):
            self.validator.check_releases_paths()

    def test_check_env_config_attrs_do_not_fail_if_empty(self, utils_mock):
        utils_mock.parse_yaml.return_value = None
        self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_fail_if_none(self, utils_mock):
        utils_mock.parse_yaml.return_value = {'attributes': None}
        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', None "
                "is not of type 'object', value path 'attributes'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_checks_metadata(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {'metadata': []}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', \[\] is "
                "not of type 'object', value path 'attributes -> metadata'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_checks_attrs(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {
                'key1': {
                    'type': True,
                    'label': 'text',
                    'value': 'text',
                    'weight': 1}}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', True is not "
                "of type 'string', value path 'attributes -> key1 -> type'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_restriction_fails(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {
                'key1': {
                    'type': 'text',
                    'label': 'test',
                    'value': 'test',
                    'weight': 1,
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        },
                        {
                            'condition': True,
                            'action': 'hide'
                        }
                    ]
                }
            }
        }

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', True is not "
                "of type 'string', value path "
                "'attributes -> key1 -> restrictions -> 1 -> condition"):
            self.validator.check_env_config_attrs()


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
