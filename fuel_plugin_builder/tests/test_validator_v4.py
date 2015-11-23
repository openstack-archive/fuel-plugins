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

from fuel_plugin_builder.tests.base import BaseValidator
from fuel_plugin_builder.validators.schemas import SchemaV4
from fuel_plugin_builder.validators.validator_v4 import ValidatorV4


class TestValidatorV4(BaseValidator):

    __test__ = True
    validator_class = ValidatorV4
    schema_class = SchemaV4

    def test_validate(self):
        mocked_methods = ['check_deployment_tasks']
        super(TestValidatorV4, self).test_validate(
            additional_mocked_methods=mocked_methods)

        self.validator.check_deployment_tasks.assert_called_once_with()

    # copy-pasted from tests v3 to
    # - override invalid base validator
    # - make additional validator class integrity smoke-test

    def test_check_schemas(self):
        mocked_methods = [
            'check_env_config_attrs',
            'validate_file_by_schema',
            'check_deployment_tasks_schema',
            'check_network_roles_schema',
            'check_node_roles_schema',
            'check_volumes_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(self.schema_class().metadata_schema,
                       self.validator.meta_path),
             mock.call(self.schema_class().tasks_schema,
                       self.validator.tasks_path, check_file_exists=False)],
            self.validator.validate_file_by_schema.call_args_list)

        self.validator.check_env_config_attrs.assert_called_once_with()
        self.validator.check_deployment_tasks_schema.assert_called_once_with()
        self.validator.check_network_roles_schema.assert_called_once_with()
        self.validator.check_node_roles_schema.assert_called_once_with()
        self.validator.check_volumes_schema.assert_called_once_with()

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
