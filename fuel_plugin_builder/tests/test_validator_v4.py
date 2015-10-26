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

    def test_check_components_schema_validation_failed(self):
        data_sets = [
            {
                'name': 'test_additional_item',
                'type': 'network',
                'label': 'test label',
                'compatible': []
            },
            {
                'name': 'test_wrong_label_type',
                'label': 1
            },
            {
                'name': 'test_wrong_description_type',
                'description': []
            },
            {
                'compatible': [],
                'incompatible': []
            },
            {
                'name': 'wrong::type_name:*',
                'compatible': [],
                'incompatible': []
            },
            {
                'name': 'storage::NameWithUpperCase',
                'label': 'Component Label'
            },
            {
                'name': 'storage::wrong_compatible_types',
                'compatible': {},
                'requires': 3,
                'incompatible': ""
            },
            {
                'name': 'storage:no_name_compatible_items',
                'incompatible': [{
                    'message': 'Component incompatible with XXX'
                }],
            },
            {
                'name': 'storage:wrong_message_compatible_items',
                'incompatible': [{
                    'name': 'storage:*',
                    'message': 1234
                }]
            },
            {
                'name': 'network:new_net:wrong_compatible',
                'compatible': [
                    {'name': ''},
                    {'name': 'wrong::component'},
                    {'name': 'storage:UpperCaseWrongName'},
                    {'name': 'Another_wrong**'}
                ]
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
                'name': 'network:test_name',
                'label': 'Test Name network'
            },
            {
                'name': 'storage:sub-type:test_name',
                'label': 'Test Storage',
                'description': 'New Test Storage Description',
                'compatible': [
                    {'name': 'hypervisor:libvirt:*'},
                    {'name': 'hypervisor:wmvare_new_1'},
                    {'name': 'network:neutron:ml2:*'},
                    {'name': 'additional_service:murano'},
                ],
                'requires': [{
                    'name': 'hypervisor:libvirt:kvm',
                    'message': 'Requires message'
                }],
                'incompatible': [
                    {
                        'name': 'storage:*',
                        'message': 'New storage is incompatible with other'
                    },
                    {
                        'name': 'additional_service:sahara',
                        'message': 'New storage is incompatible with Sahara'
                    }
                ]
            },
            {
                'name': 'hypervisor:new',
                'label': 'New Hypervisor',
                'compatible': []
            },
            {
                'name': 'additional_service:ironic-new',
                'label': 'Ironic New',
                'incompatible': [{
                    'name': 'additional_service:*',
                    'message': 'Alert message'
                }],
                'requires': [{
                    'name': 'storage:test'
                }]
            }
        ]

        with mock.patch('fuel_plugin_builder.validators.base.utils') \
                as mock_utils:
            for data in data_sets:
                mock_utils.parse_yaml.return_value = [data]
                self.validator.check_components_schema()
