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
from fuel_plugin_builder.validators.schemas import SchemaV3
from fuel_plugin_builder.validators.validator_v3 import ValidatorV3


class TestValidatorV3(BaseValidator):

    __test__ = True
    validator_class = ValidatorV3
    schema_class = SchemaV3

    def test_validate(self):
        mocked_methods = ['check_deployment_tasks']
        super(TestValidatorV3, self).test_validate(
            additional_mocked_methods=mocked_methods)

        self.validator.check_deployment_tasks.assert_called_once_with()

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
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': 'xx',
                    'puppet_modules': 'yy',
                    'retries': 'asd',
                },
                'stage': 'post_deployment',
                'role': '*'
            }
        ]

        with mock.patch('fuel_plugin_builder.validators.validator_v3.utils') \
                as mock_utils:
            for data in data_sets:
                mock_utils.parse_yaml.return_value = [data]
                self.assertRaises(errors.ValidationError,
                                  self.validator.check_deployment_tasks)

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
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
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
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
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
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'retries': 10,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
            ]
        ]

        with mock.patch('fuel_plugin_builder.validators.validator_v3.utils') \
                as mock_utils:
            for data in data_sets:
                mock_utils.parse_yaml.return_value = data
                self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_tasks_no_file(self, exists_mock, utils_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_deployment_tasks()
        self.assertFalse(self.validator.validate_schema.called)

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

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_group_type_deployment_task(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'group',
            'groups': ['plugin_name']}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/deployment_tasks.yaml', "
                "'role' is a required property, value path '0'"):
            self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_puppet_type_deployment_task(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'puppet'}]

        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_skipped_type_deployment_task(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'skipped'}]

        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_group_type_deployment_task_does_not_contain_manifests(
            self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': ['plugin_name'],
            'parameters': {}}]

        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_deployment_task_role_failed(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': ['plugin_n@me']}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/deployment_tasks.yaml',"
                " 'plugin_n@me' does not match"):
            self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    def test_check_deployment_task_role(self, utils_mock):
        utils_mock.parse_yaml.return_value = [
            {'id': 'plugin_name', 'type': 'group', 'role': []},
            {'id': 'plugin_name', 'type': 'group', 'role': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'group', 'role': '*'},
            {'id': 'plugin_name', 'type': 'puppet', 'role': []},
            {'id': 'plugin_name', 'type': 'puppet', 'role': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'puppet', 'role': '*'},
            {'id': 'plugin_name', 'type': 'shell', 'role': []},
            {'id': 'plugin_name', 'type': 'shell', 'role': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'shell', 'role': '*'},
            {'id': 'plugin_name', 'type': 'skipped', 'role': []},
            {'id': 'plugin_name', 'type': 'skipped', 'role': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'skipped', 'role': '*'},
        ]

        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_deployment_task_id(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_n@me',
            'type': 'group',
            'role': ['plugin_name']}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/deployment_tasks.yaml',"
                " 'plugin_n@me' does not match"):
            self.validator.check_deployment_tasks_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_deployment_task_valid_dependencies(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': ['plugin_name'],
            'requires': ['dependency_1', 'dependency_2']}]

        self.validator.check_deployment_tasks_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_deployment_task_invalid_dependencies(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': ['plugin_name'],
            'requires': ['dependency_1', 'dependency_#']}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/deployment_tasks.yaml',"
                " 'dependency_#' does not match"):
            self.validator.check_deployment_tasks_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_node_roles_have_correct_name(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'plug$n_n@me': {
                'name': 'test_plugin',
                'description': 'test plugin'}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/node_roles.yaml', Additional"
                " properties are not allowed"):
            self.validator.check_node_roles_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_node_role_should_has_name(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'plugin_name': {
                'description': 'test plugin'}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/node_roles.yaml', 'name' is"
                " a required property, value path 'plugin_name'"):
            self.validator.check_node_roles_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_valid_volumes_roles_mapping_name(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'volumes_roles_mapping': {
                'mapping_name': [{'allocate_size': 'min', 'id': 'test'}]},
            'volumes': []}

        self.validator.check_volumes_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_invalid_volumes_roles_mapping_name(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'volumes_roles_mapping': {
                'm@pping_name': [{'allocate_size': 'min', 'id': 'test'}]},
            'volumes': []}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/volumes.yaml', Additional"
                " properties are not allowed"):
            self.validator.check_volumes_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_valid_network_roles(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            "id": "example_net_role",
            "default_mapping": "public",
            "properties": {
                "subnet": True,
                "gateway": False,
                "vip": [{
                    "name": "vip_name",
                    "namespace": "haproxy"}]}}]

        self.validator.check_network_roles_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_network_roles_vip_have_invalid_name(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            "id": "example_net_role",
            "default_mapping": "public",
            "properties": {
                "subnet": True,
                "gateway": False,
                "vip": [{
                    "name": "vip@name",
                    "namespace": "haproxy"}]}}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/network_roles.yaml',"
                " 'vip@name' does not match"):
            self.validator.check_network_roles_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_network_roles_vip_have_invalid_namespace(self, utils_mock):
        utils_mock.parse_yaml.return_value = [{
            "id": "example_net_role",
            "default_mapping": "public",
            "properties": {
                "subnet": True,
                "gateway": False,
                "vip": [{
                    "name": "vip_name",
                    "namespace": "hap roxy"}]}}]

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/network_roles.yaml',"
                " 'hap roxy' does not match"):
            self.validator.check_network_roles_schema()
