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

from fuel_plugin_builder.tests.test_validator_v4 import TestValidatorV4
from fuel_plugin_builder.validators.schemas import SchemaV5
from fuel_plugin_builder.validators.validator_v5 import ValidatorV5


class TestValidatorV5(TestValidatorV4):

    __test__ = True
    validator_class = ValidatorV5
    schema_class = SchemaV5

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_failed(self, utils_mock):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0']),
            (['6.1', '7.0', '8.0']),
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0']),
            (['7.0']),
        )

        for fuel_version in fuel_version_checks:
            mock_data = {
                'fuel_version': fuel_version,
                'package_version': '5.0.0'}
            err_msg = 'Current plugin format 5.0.0 is not compatible with ' \
                      '{0} Fuel release. Fuel version must be 8.0 or higher.' \
                      ' Please remove {0} version from metadata.yaml file or' \
                      ' downgrade package_version.'.format(fuel_version[0])

            self.check_raised_exception(
                utils_mock, mock_data,
                err_msg, self.validator.check_compatibility)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_passed(self, utils_mock):
        fuel_version_checks = (
            (['8.0']),
            (['9.0']),
            (['8.0', '9.0']),
        )
        for fuel_version in fuel_version_checks:
            mock_data = {
                'fuel_version': fuel_version,
                'package_version': '5.0.0'}
            utils_mock.parse_yaml.return_value = mock_data
            self.validator.check_compatibility()

    def test_check_deployment_task_invalid_dependencies(self, *args, **kwargs):
        # todo write tests
        pass

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_is_hotpluggable_flag(self, utils_mock):
        mock_data = {
            'name': 'plugin_name-12',
            'title': 'plugin_name-12',
            'version': '1.2.3',
            'package_version': '5.0.0',
            'description': 'Description',
            'fuel_version': ['9.0.0'],
            'licenses': ['Apache', 'BSD'],
            'authors': ['Author1', 'Author2'],
            'homepage': 'http://test.com',
            'releases': [
                {
                    "os": "ubuntu",
                    "version": "liberty-8.0",
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
