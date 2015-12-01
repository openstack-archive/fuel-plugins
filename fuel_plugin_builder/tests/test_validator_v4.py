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
from fuel_plugin_builder.tests.test_validator_v3 import TestValidatorV3
from fuel_plugin_builder.validators.schemas import SchemaV4
from fuel_plugin_builder.validators.validator_v4 import ValidatorV4


class TestValidatorV4(TestValidatorV3):

    __test__ = True
    validator_class = ValidatorV4
    schema_class = SchemaV4

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_failed(self, utils_mock):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0']),
            (['6.1', '7.0', '8.0']),
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0']),
        )

        for fuel_version in fuel_version_checks:
            mock_data = {
                'fuel_version': fuel_version,
                'package_version': '4.0.0'}
            err_msg = 'Current plugin format 4.0.0 is not compatible with ' \
                      '{0} Fuel release. Fuel version must be 8.0 or higher.' \
                      ' Please remove {0} version from metadata.yaml file or' \
                      ' downgrade package_version.'.format(fuel_version[0])

            self.check_raised_exception(
                utils_mock, mock_data,
                err_msg, self.validator.check_compatibility)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_passed(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['8.0'],
            'package_version': '4.0.0'}
        self.validator.check_compatibility()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_is_hotpluggable_flag(self, utils_mock):
        mock_data = {
            'name': 'plugin_name-12',
            'title': 'plugin_name-12',
            'version': '1.2.3',
            'package_version': '4.0.0',
            'description': 'Description',
            'fuel_version': ['8.0.0'],
            'licenses': ['Apache', 'BSD'],
            'authors': ['Author1', 'Author2'],
            'homepage': 'http://test.com',
            'releases': [
                {
                    "os": "ubuntu",
                    "version": "2015.1-8.0",
                    "mode": ['ha'],
                    "deployment_scripts_path": "deployment_scripts/",
                    "repository_path": "repositories/ubuntu"
                }
            ],
            'groups': ['network'],
            'is_hotpluggable': True
        }
        utils_mock.parse_yaml.return_value = mock_data
        self.assertEqual(None, self.validator.check_metadata_schema())

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_environment_config_settings_groups(self, utils_mock):
        mock_data = {'attributes': {}}
        utils_mock.parse_yaml.return_value = mock_data
        self.assertEqual(None, self.validator.check_env_config_attrs())

        mock_data = {'attributes': {'metadata': {}}}
        utils_mock.parse_yaml.return_value = mock_data
        self.assertEqual(None, self.validator.check_env_config_attrs())

        mock_data = {'attributes': {'metadata': {'group': 'network'}}}
        utils_mock.parse_yaml.return_value = mock_data
        self.assertEqual(None, self.validator.check_env_config_attrs())

        mock_data = {'attributes': {'metadata': {'group': 'unknown'}}}
        utils_mock.parse_yaml.return_value = mock_data
        self.assertRaises(
            errors.ValidationError,
            self.validator.check_env_config_attrs
        )
