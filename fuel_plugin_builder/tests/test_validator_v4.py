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

    def test_check_schemas(self):
        mocked_methods = [
            'check_env_config_attrs',
            'check_deployment_tasks_schema',
            'check_network_roles_schema',
            'check_node_roles_schema',
            'check_volumes_schema',
            'check_components_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.mock_methods(self.validator, ['validate_file_by_schema'])
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(self.schema_class().metadata_schema,
                       self.validator.meta_path),
             mock.call(self.schema_class().tasks_schema,
                       self.validator.tasks_path, check_file_exists=False)],
            self.validator.validate_file_by_schema.call_args_list)

        for method in mocked_methods:
            getattr(self.validator, method).assert_called_once_with()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_failed(self, utils_mock):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0', '8.0']),
        )

        for fuel_version in fuel_version_checks:
            mock_data = {
                'fuel_version': fuel_version,
                'package_version': '4.0.0'}
            utils_mock.parse_yaml.return_value = mock_data
            with self.assertRaisesRegexp(
                    errors.ValidationError,
                    'Current plugin format 4.0.0 is not compatible with '
                    '{0} Fuel release. Fuel version must be 8.0 or higher. '
                    'Please remove {0} version from metadata.yaml file or '
                    'downgrade package_version.'.format(fuel_version[0])):
                self.validator.check_compatibility()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_passed(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['8.0'],
            'package_version': '4.0.0'}
        self.validator.check_compatibility()

    def test_check_components_schema_validation_failed(self):
        data_sets = [
            {
                'name': 'test_without_type',
                'compatible': {}
            },
            {
                'type': 'network',
                'compatible': {}
            },
            {
                'name': '',
                'type': 'network',
                'compatible': {}
            },
            {
                'name': 'wrong::Name_format:',
                'type': 'storage',
                'compatible': {}
            },
            {
                'name': 'test_name',
                'type': 'unexpected_type',
                'compatible': {}
            },
            {
                'name': 'unexpected_additional_property',
                'type': 'hypervisor',
                'compatible': {
                    'networks': [],
                    'storages': [],
                    'additional_property': []
                }
            },
            {
                'name': 'wrong_compatibility_names',
                'type': 'additional_service',
                'compatible': {
                    'networks': [':', ':wrong::component', 'Another%wrong%']
                }
            }
        ]

        with mock.patch('fuel_plugin_builder.validators.base.utils') as \
                mock_utils:
            for data in data_sets:
                mock_utils.parse_yaml.return_value = [data]
                self.assertRaises(errors.ValidationError,
                                  self.validator.check_components_schema)

    def test_check_components_schema_validation_passed(self):
        data_sets = [
            {
                'name': 'test_name',
                'type': 'network'
            },
            {
                'name': 'sub-type:test_name',
                'type': 'storage',
                'compatible': {}
            },
            {
                'name': 'test_all_subtype_compatibility',
                'type': 'hypervisor',
                'compatible': {
                    'networks': ['*']
                }
            },
            {
                'name': 'neutron:core:ml2:ovs',
                'type': 'network',
                'compatible': {
                    'storages': [],
                    'networks': ['neutron:core:ml2', 'neutron:service'],
                    'additional_services': ['*']
                }
            },
            {
                'name': 'ironic',
                'type': 'additional_service',
                'compatible': {
                    'hypervisors': ['*'],
                    'networks': ['neutron:service:l2'],
                    'storages': ['object:backend', 'block:backend'],
                    'additional_services': ['*']
                }
            }
        ]

        with mock.patch('fuel_plugin_builder.validators.base.utils') \
                as mock_utils:
            for data in data_sets:
                mock_utils.parse_yaml.return_value = [data]
                self.validator.check_components_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists',
                return_value=False)
    def test_components_file_exist_validation(self, mock_utils):
        with self.assertRaises(errors.FileDoesNotExist):
            self.validator.check_components_schema()
