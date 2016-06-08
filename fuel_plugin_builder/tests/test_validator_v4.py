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

    def setUp(self):
        super(TestValidatorV4, self).setUp()
        self.metadata = {
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
                    "version": "liberty-8.0",
                    "mode": ['ha'],
                    "deployment_scripts_path": "deployment_scripts/",
                    "repository_path": "repositories/ubuntu"
                }
            ],
            'groups': [],
            'is_hotpluggable': False
        }

    def test_check_schemas(self):
        mocked_methods = [
            'check_metadata_schema',
            'check_env_config_attrs',
            'check_tasks_schema',
            'check_deployment_tasks_schema',
            'check_network_roles_schema',
            'check_node_roles_schema',
            'check_volumes_schema',
            'check_components_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.mock_methods(self.validator, ['validate_file_by_schema'])
        self.validator.check_schemas()

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

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_components_schema_validation_failed(self, utils_mock):
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

        for data in data_sets:
            utils_mock.parse_yaml.return_value = [data]
            self.assertRaises(errors.ValidationError,
                              self.validator.check_components_schema)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_components_schema_validation_passed(self, utils_mock):
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
                'bind': [('some_key', 'some_val')],
                'incompatible': [{
                    'name': 'additional_service:*',
                    'message': 'Alert message'
                }],
                'requires': [{
                    'name': 'storage:test'
                }]
            }
        ]

        for data in data_sets:
            utils_mock.parse_yaml.return_value = [data]
            self.validator.check_components_schema()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_groups(self, utils_mock):
        groups_data = [
            ["network"],
            ["storage"],
            ["storage::cinder"],
            ["storage::glance"],
            ["hypervisor"],
            ["equipment"],
            ["storage::cinder", "equipment"],
            []
        ]
        for gd in groups_data:
            self.metadata['groups'] = gd
            utils_mock.parse_yaml.return_value = self.metadata
            self.assertEqual(None, self.validator.check_metadata_schema())

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_deployment_task_reexecute_on(self, utils_mock):
        mock_data = [{
            'id': 'plugin_task',
            'type': 'puppet',
            'groups': ['controller'],
            'reexecute_on': ['bla']}]
        err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
                  "'bla' is not one of"
        self.check_raised_exception(
            utils_mock, mock_data,
            err_msg, self.validator.check_deployment_tasks_schema)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    @mock.patch('fuel_plugin_builder.validators.validator_v4.logger')
    def test_role_attribute_is_required_for_deployment_task_types(
            self, logger_mock, utils_mock, *args):
        deployment_tasks_data = [
            {
                'id': 'plugin_name',
                'type': 'group'
            },
            {
                'id': 'plugin_name',
                'type': 'shell'
            },
            {
                'id': 'plugin_name',
                'type': 'copy_files',
                'parameters': {
                    'files': [{'src': '/dev/null', 'dst': '/dev/null'}]
                }
            },
            {
                'id': 'plugin_name',
                'type': 'sync',
                'parameters': {'src': '/dev/null', 'dst': '/dev/null'}
            },
            {
                'id': 'plugin_name',
                'type': 'upload_file',
                'parameters': {
                    'path': 'http://test.com',
                    'data': 'VGVzdERhdGE='
                }
            }
        ]

        for task in deployment_tasks_data:
            utils_mock.parse_yaml.return_value = [task]
            logger_mock.warn.reset_mock()
            self.validator.check_deployment_tasks()
            self.assertEqual(logger_mock.warn.call_count, 1)

    # This is the section of tests inherited from the v3 validator
    # where decorators is re-defined for module v4

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_tasks_no_file(self, exists_mock, utils_mock, *args):
        super(TestValidatorV4, self).test_check_deployment_task_role(
            exists_mock, utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_deployment_task_role(self, utils_mock, *args):
        utils_mock.parse_yaml.return_value = [
            {'id': 'plugin_name', 'type': 'group', 'groups': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'group', 'groups': '*'},
            {'id': 'plugin_name', 'type': 'puppet', 'role': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'puppet', 'role': '*'},
            {'id': 'plugin_name', 'type': 'shell', 'roles': ['a', 'b']},
            {'id': 'plugin_name', 'type': 'shell', 'roles': '*'},
            {'id': 'plugin_name', 'type': 'skipped', 'role': '/test/'},
            {'id': 'plugin_name', 'type': 'stage'},
            {'id': 'plugin_name', 'type': 'reboot', 'groups': 'contrail'},
            {
                'id': 'plugin_name',
                'type': 'copy_files',
                'role': '*',
                'parameters': {
                    'files': [
                        {'src': 'some_source', 'dst': 'some_destination'}]}
            },
            {
                'id': 'plugin_name',
                'type': 'sync',
                'role': 'plugin_name',
                'parameters': {
                    'src': 'some_source', 'dst': 'some_destination'}
            },
            {
                'id': 'plugin_name',
                'type': 'upload_file',
                'role': '/^.*plugin\w+name$/',
                'parameters': {
                    'path': 'some_path', 'data': 'some_data'}
            },
        ]

        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_deployment_task_role_failed(self, utils_mock, *args):
        mock_data = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': ['plugin_n@me']}]
        err_msg = "field should"
        self.check_raised_exception(
            utils_mock, mock_data,
            err_msg, self.validator.check_deployment_tasks)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_deployment_task_required_missing(self, utils_mock, *args):
        mock_data = [{
            'groups': 'plugin_name',
            'type': 'puppet'}]
        err_msg = 'required'
        self.check_raised_exception(
            utils_mock, mock_data,
            err_msg, self.validator.check_deployment_tasks)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_deployment_task_required_roles_missing_is_ok(
            self, utils_mock, *args):
        utils_mock.parse_yaml.return_value = [{
            'id': 'plugin_name',
            'type': 'stage'}]
        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_deployment_task_role_regexp_failed(self, utils_mock, *args):
        mock_data = [{
            'id': 'plugin_name',
            'type': 'group',
            'role': '/[0-9]++/'}]
        err_msg = "field should.*multiple repeat"
        self.check_raised_exception(
            utils_mock, mock_data,
            err_msg, self.validator.check_deployment_tasks)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_group_type_deployment_task_does_not_contain_manifests(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_check_group_type_deployment_task_does_not_contain_manifests(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_files_attribute_is_required_for_copy_files_task_type(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_files_attribute_is_required_for_copy_files_task_type(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_files_should_contain_at_least_one_item_for_copy_files_task_type(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_files_should_contain_at_least_one_item_for_copy_files_task_type(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_parameters_attribute_is_required_for_deployment_task_types(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_parameters_attribute_is_required_for_deployment_task_types(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_path_and_data_attributes_are_required_for_upload_file_task_type(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_path_and_data_attributes_are_required_for_upload_file_task_type(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_src_and_dst_attributes_are_required_for_copy_files_task_type(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_src_and_dst_attributes_are_required_for_copy_files_task_type(
            utils_mock)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_src_and_dst_attributes_are_required_for_sync_task_type(
            self, utils_mock, *args):
        super(
            TestValidatorV4, self
        ).test_src_and_dst_attributes_are_required_for_sync_task_type(
            utils_mock)

    # todo(ikutukov): validation for old-style tasks.yaml without
    # id and normal dependencies. Have to find out what to do with them.

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_validation_failed(self, utils_mock, *args):
        pass

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_validation_passed(self, utils_mock, *args):
        pass

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_1_0_validation_failed(self, utils_mock, *args):
        checks = [
            {
                'data': {
                    'id': 'task-id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                'errorTextContains': "'cmd' is a required property, "
                                     "value path '0 -> parameters'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                'errorTextContains': "'puppet_manifest' is a required property"
                                     ", value path '0 -> parameters'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                'errorTextContains': "'puppet_manifest' is a required property"
                                     ", value path '0 -> parameters'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'yy',
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                'errorTextContains': "'cmd' is a required property, value path"
                                     " '0 -> parameters'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'yy',
                        'retries': 'asd',
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                'errorTextContains': "'asd' is not of type 'integer', value "
                                     "path '0 -> parameters -> retries'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': '',
                        'retries': 1,
                    },
                    'stage': 'pre_deployment',
                    'role': '*'
                },
                'errorTextContains': "'' is too short, value path '0 -> "
                                     "parameters -> puppet_modules'"
            },
            {
                'data': {
                    'id': 'task-id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': '',
                        'puppet_modules': 'yy',
                        'retries': 1,
                    },
                    'stage': 'pre_deployment',
                    'role': '*'
                },
                'errorTextContains': "'' is too short, value path '0 -> "
                                     "parameters -> puppet_manifest'"
            }
        ]

        for check in checks:
            utils_mock.parse_yaml.return_value = [check['data']]
            self.assertRaisesRegexp(
                errors.ValidationError,
                check['errorTextContains'],
                self.validator.check_deployment_tasks)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_1_0_validation_passed(self, utils_mock, *args):
        data_sets = [
            [
                {
                    'id': 'task_id',
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
                    'id': 'task_id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'task_id',
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
                    'id': 'task_id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'task_id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'task_id',
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
                    'id': 'task_id',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'task_id',
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
                    'id': 'task_id',
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
                {
                    'id': 'task_id',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'retries': 10,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': 'master'
                },
            ]
        ]

        for data in data_sets:
            utils_mock.parse_yaml.return_value = data
            self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_2_0_validation_failed(self, utils_mock, *args):
        tasks_data = [
            {
                'id': 'test',
                'type': 'shell',
                'version': '2'
            },
            {
                'id': 'test',
                'type': 'shell',
                'cross-depends': [
                    {
                        'role': 'role_without_name'
                    }
                ]
            },
            {
                'id': 'test',
                'type': 'shell',
                'parameters': {
                    'strategy': 'NOSUCHSTRATEGY'
                }
            },
            {
                'id': 'test',
                'type': 'shell',
                'parameters': {
                    'strategy': {
                        'type': 'NOSUCHSTRATEGY'
                    }
                }
            }
        ]

        utils_mock.parse_yaml.return_value = tasks_data
        self.assertRaises(errors.ValidationError,
                          self.validator.check_deployment_tasks)

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_2_0_validation_passed(self, utils_mock, *args):
        tasks_data = [
            {
                'id': 'task_id',
                'type': 'puppet',
                'version': '2.0.0',
                'parameters': {
                    'timeout': 3,
                    'retries': 10,
                    'puppet_manifest': 'xx',
                    'puppet_modules': 'xxx'
                },
                'stage': 'post_deployment',
                'roles': ['test_role'],
                'cross-depends': [
                    {
                        'name': 'task_id2',
                    },
                    {
                        'name': 'task_id2',
                        'role': ['some_role']
                    },
                    {
                        'name': 'task_id2',
                        'role': 'some_role'
                    },
                    {
                        'name': 'task_id2',
                        'policy': 'all'
                    },
                    {
                        'name': 'task_id2',
                        'policy': 'any'
                    }
                ],
                'cross-depended-by': [
                    {
                        'name': 'task_id2',
                    },
                    {
                        'name': 'task_id2',
                        'role': ['some_role']
                    },
                    {
                        'name': 'task_id2',
                        'role': 'some_role'
                    },
                    {
                        'name': 'task_id2',
                        'policy': 'all'
                    },
                    {
                        'name': 'task_id2',
                        'policy': 'any'
                    }
                ],
                'strategy': {
                    'type': 'parallel',
                    'amount': 10
                }
            }
        ]

        utils_mock.parse_yaml.return_value = tasks_data
        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.validator_v4.utils')
    def test_check_tasks_schema_2_1_validation_passed(self, utils_mock, *args):
        # this is a slightly modified task from netconfig.yaml
        tasks_data = [
            {
                "id": "netconfig",
                "type": "puppet",
                "version": "2.1.0",
                "groups": [
                    "primary-controller",
                    "controller",
                ],
                "required_for": [
                    "deploy_end"
                ],
                "requires": [
                    "tools"
                ],
                "condition": {
                    "yaql_exp": "changedAny($.network_scheme, $.dpdk, $.get('"
                                "use_ovs'), $.get('set_rps'), $.get('set_rps')"
                                ", $.get('run_ping_checker'), $.network_scheme"
                                ".endpoints.values().where(\n  $.get('gateway'"
                                ") != null).gateway)\n"
                },
                "parameters": {
                    "puppet_manifest": "/etc/puppet/modules/osnailyfacter/"
                                       "modular/netconfig/netconfig.pp",
                    "puppet_modules": "/etc/puppet/modules",
                    "timeout": 300,
                    "strategy": {
                        "type": "parallel",
                        "amount": {
                            "yaql_exp": "switch($.get('deployed_before', {})."
                                        "get('value') => 1, true => 3)\n"
                        }
                    }
                },
                "test_pre": {
                    "cmd": "ruby /etc/puppet/modules/osnailyfacter/modular/"
                           "netconfig/netconfig_pre.rb"
                },
                "test_post": {
                    "cmd": "ruby /etc/puppet/modules/osnailyfacter/modular/"
                           "netconfig/netconfig_post.rb"
                },
                "cross-depends": {
                    "yaql_exp": "switch(   (\n    $.roles.any($.matches('("
                                "primary-)?(controller|mongo)'))\n    "
                                "or ($.network_metadata.get('vips',{}).get"
                                "('management') = null)\n  ) => [],\n  "
                                "true => [{name =>'virtual_ips'}]\n)\n"
                }
            }
        ]

        utils_mock.parse_yaml.return_value = tasks_data
        self.validator.check_deployment_tasks()

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_tasks_schema_validation_no_file(self, exists_mock, *args):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_tasks_schema()
        self.assertFalse(self.validator.validate_schema.called)
