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
from fuel_plugin_builder.validators import ValidatorV1

from fuel_plugin_builder.validators.schemas.v1 import SchemaV1


class TestValidatorV1(BaseTestCase):

    def setUp(self):
        self.plugin_path = '/tmp/plugin_path'
        self.validator = ValidatorV1(self.plugin_path)

    @mock.patch.object(ValidatorV1, 'check_schemas')
    @mock.patch.object(ValidatorV1, 'check_tasks')
    @mock.patch.object(ValidatorV1, 'check_releases_paths')
    @mock.patch.object(ValidatorV1, 'check_compatibility')
    def test_validate(
            self,
            check_tasks_mock,
            check_schemas_mock,
            check_paths_mock,
            check_compatibility_mock):
        self.validator.validate()
        check_tasks_mock.assert_called_once_with()
        check_schemas_mock.assert_called_once_with()
        check_paths_mock.assert_called_once_with()
        check_compatibility_mock.assert_called_once_with()

    @mock.patch.object(ValidatorV1, 'check_env_config_attrs')
    @mock.patch.object(ValidatorV1, 'validate_file_by_schema')
    def test_check_schemas(self, validator_mock, check_env_conf_mock):
        self.validator.check_schemas()
        self.assertEqual(
            [mock.call(
                SchemaV1().metadata_schema,
                self.validator.meta_path),
             mock.call(
                 SchemaV1().tasks_schema,
                 self.validator.tasks_path)],
            validator_mock.call_args_list)
        check_env_conf_mock.assert_called_once_with()

    @mock.patch.object(ValidatorV1, 'validate_schema')
    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
    def test_check_tasks(self, utils_mock, validate_schema_mock):
        utils_mock.parse_yaml.return_value = [
            {'type': 'puppet', 'parameters': 'param1'},
            {'type': 'shell', 'parameters': 'param2'}]

        self.validator.check_tasks()

        self.assertEqual(
            [mock.call('param1', SchemaV1().puppet_parameters,
                       self.validator.tasks_path,
                       value_path=[0, 'parameters']),
             mock.call('param2', SchemaV1().shell_parameters,
                       self.validator.tasks_path,
                       value_path=[1, 'parameters'])],
            validate_schema_mock.call_args_list)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
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

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_releases_paths_error(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': '/tmp/repository_path'}]}

        utils_mock.exists.return_value = False
        with self.assertRaisesRegexp(
                errors.ReleasesDirectoriesError,
                'Cannot find directories /tmp/deployment_scripts_path'
                ', /tmp/repository_path for release "'):
            self.validator.check_releases_paths()

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils.parse_yaml')
    def test_check_env_config_attrs_do_not_fail_if_empty(
            self, parse_yaml_mock):
        parse_yaml_mock.return_value = None
        self.validator.check_env_config_attrs()

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils.parse_yaml')
    def test_check_env_config_attrs_fail_if_none(self, parse_yaml_mock):
        parse_yaml_mock.return_value = {'attributes': None}
        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', None "
                "is not of type 'object', value path 'attributes'"):
            self.validator.check_env_config_attrs()

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils.parse_yaml')
    def test_check_env_config_attrs_checks_metadata(self, parse_yaml_mock):
        parse_yaml_mock.return_value = {
            'attributes': {'metadata': []}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', \[\] is "
                "not of type 'object', value path 'attributes -> metadata'"):
            self.validator.check_env_config_attrs()

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils.parse_yaml')
    def test_check_env_config_attrs_checks_attrs(self, parse_yaml_mock):
        parse_yaml_mock.return_value = {
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

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils.parse_yaml')
    def test_check_compatibility(self, parse_yaml_mock):
        parse_yaml_mock.return_value = {
            'fuel_version': ['5.1', '6.0', '6.1'],
            'package_version': '1.0.0'}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                'Current plugin format 1.0.0 is not compatible with 5.1 Fuel'
                ' release. Fuel version must be 6.0 or higher.'
                ' Please remove 5.1 version from metadata.yaml file or'
                ' downgrade package_version.'):
            self.validator.check_compatibility()
