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

from fuel_plugin_builder.validators.schemas import v1


class TestValidatorV1(BaseTestCase):

    def setUp(self):
        self.plugin_path = '/tmp/plugin_path'
        self.validator = ValidatorV1(self.plugin_path)

    @mock.patch.object(ValidatorV1, 'check_schemas')
    @mock.patch.object(ValidatorV1, 'check_tasks')
    @mock.patch.object(ValidatorV1, 'check_releases_paths')
    def test_validate(
            self, check_tasks_mock, check_schemas_mock, check_paths_mock):
        self.validator.validate()
        check_tasks_mock.assert_called_once_with()
        check_schemas_mock.assert_called_once_with()
        check_paths_mock.assert_called_once_with()

    @mock.patch.object(ValidatorV1, 'validate_file_by_schema')
    def test_check_schemas(self, validator_mock):
        self.validator.check_schemas()
        self.assertEqual(
            [mock.call(
                v1.METADATA_SCHEMA,
                self.validator.meta_path),
             mock.call(
                 v1.TASKS_SCHEMA,
                 self.validator.tasks_path),
             mock.call(
                 v1.ENV_CONFIG_SCHEMA,
                 self.validator.env_conf_path)],
            validator_mock.call_args_list)

    @mock.patch.object(ValidatorV1, 'validate_schema')
    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
    def test_check_tasks(self, utils_mock, validate_schema_mock):
        utils_mock.parse_yaml.return_value = [
            {'type': 'puppet', 'parameters': 'param1'},
            {'type': 'shell', 'parameters': 'param2'}]

        self.validator.check_tasks()

        self.assertEqual(
            [mock.call('param1', v1.PUPPET_PARAMETERS,
                       self.validator.tasks_path),
             mock.call('param2', v1.SHELL_PARAMETERS,
                       self.validator.tasks_path)],
            validate_schema_mock.call_args_list)

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
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

    @mock.patch('fuel_plugin_builder.validators.validator_v1.utils')
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
