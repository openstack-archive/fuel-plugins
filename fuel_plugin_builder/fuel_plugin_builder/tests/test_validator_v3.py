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
from fuel_plugin_builder.validators.schemas.v3 import SchemaV3
from fuel_plugin_builder.validators.validator_v3 import ValidatorV3


class TestValidatorV3(BaseValidator):

    __test__ = True
    validator_class = ValidatorV3
    schema_class = SchemaV3

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_network_roles(self, utils_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        utils_mock.parse_yaml.return_value = [{
            'id': 1,
            'default_mapping': 'xx',
            'properties': {
                'subnet': True, 'gateway': True,
                'vip': [{'name': 'a'}]
            }
        }]

        self.validator.check_network_roles()
        self.assertFalse(self.validator.validate_schema.called)

    def test_check_tasks_schema_validation_failed(self):
        data_sets = [
            {
                'type': 'shell',
                'parameters': {
                    'timeout': 3
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'cmd': 'xx'
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'shell',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': 'xx',
                    'puppet_modules': 'yy',
                },
                'stage': 'post_deployment',
                'role': '*'
            }
        ]

        with mock.patch.object(self.validator, '_parse_tasks') as \
                parse_tasks_mock:
            for data in data_sets:
                parse_tasks_mock.return_value = [data]
                self.assertRaises(errors.ValidationError,
                                  self.validator.check_tasks)

    def test_check_tasks_schema_validation_passed(self):
        data_sets = [
            [
                {
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
            ],
            [
                {
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
            ],
            [
                {
                    'type': 'reboot',
                    'parameters': {
                        'timeout': 3,
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                }
            ],
            [
                {
                    'type': 'reboot',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'type': 'reboot',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'yy',
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                }
            ]
        ]

        with mock.patch.object(self.validator, '_parse_tasks') as \
                parse_tasks_mock:
            for data in data_sets:
                parse_tasks_mock.return_value = data
                self.validator.check_tasks()

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_network_roles_no_file(self, exists_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_network_roles()
        self.assertFalse(self.validator.validate_schema.called)

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_tasks_no_file(self, exists_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_tasks()
        self.assertFalse(self.validator.validate_schema.called)

    def test_check_schemas(self):
        mocked_methods = [
            'check_env_config_attrs',
            'validate_file_by_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(
                self.schema_class().metadata_schema,
                self.validator.meta_path)],
            self.validator.validate_file_by_schema.call_args_list)
        self.validator.check_env_config_attrs.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_failed(self, utils_mock):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0']),
        )

        for fuel_version in fuel_version_checks:
            version_in_msg = fuel_version[0]
            utils_mock.parse_yaml.return_value = {
                'fuel_version': fuel_version,
                'package_version': '3.0.0'}

            with self.assertRaisesRegexp(
                    errors.ValidationError,
                    'Current plugin format 3.0.0 is not compatible with {0}'
                    ' Fuel release. Fuel version must be 7.0 or higher.'
                    ' Please remove {0} version from metadata.yaml file or'
                    ' downgrade package_version.'.format(version_in_msg)):
                self.validator.check_compatibility()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_passed(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['7.0'],
            'package_version': '3.0.0'}
        self.validator.check_compatibility()

    def test_validate(self):
        mocked_methods = [
            'check_network_roles',
        ]
        self.mock_methods(self.validator, mocked_methods)
        super(TestValidatorV3, self).test_validate()
        self.validator.check_network_roles.assert_called_once_with()
