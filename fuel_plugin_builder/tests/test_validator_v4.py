# -*- coding: utf-8 -*-

#    Copyright 2016 Mirantis, Inc.
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
import os
from copy import deepcopy

import mock
import six
import yaml

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.validators import ValidatorV4
from pyfakefs import fake_filesystem_unittest


class TestExectutionResult(object):
    def __init__(self, process_handle, out, err):
        self.return_code = process_handle.returncode
        self.stdout = out
        self.stderr = err

    @property
    def has_errors(self):
        return self.return_code != 0

    @property
    def is_return_code_zero(self):
        return self.return_code == 0


class TestValidatorV4(fake_filesystem_unittest.TestCase, TestExectutionResult):
    default_mock_path = './examples/fuel_plugin_example_v4/'

    def _make_absolute_path(self, relative_path):
        """Make absolute path related to the plugin example root folder.

        :param relative_path: relative path
        :type relative_path: basestring
        :return: absolute path
        :rtype: basestring
        """
        return os.path.join(self.default_mock_path, relative_path)

    def _make_metadata(self, **kwargs):
        """Generate metadata based on example and custom fields from kwargs.

        :return: metadata
        :rtype: dict
        """
        metadata = deepcopy(self.metadata_example or {})
        metadata.update(kwargs)
        return metadata

    def _replace_yaml_file(self, path, new_data):
        """Replace file with new one inside file system mock.

        :param path: relative path
        :type path: basestring
        :param new_data: list/dict structure that will be serialised to YAML
        :type new_data: dict|list
        """
        self.fs.RemoveObject(self._make_absolute_path(path))
        self.fs.CreateFile(
                self._make_absolute_path(path),
                contents=yaml.dump(new_data))

    def setUp(self):
        for root, dir_names, file_names in os.walk(self.default_mock_path):
            for filename in file_names:
                file_path = os.path.join(root, filename)
                with open(file_path) as f:
                    self.fs.CreateFile(
                        file_path,
                        contents=f.read())
        self.metadata_example = yaml.load(
            open(self._make_absolute_path('metadata.yaml')).read()
        )
        self.validator = ValidatorV4(self.default_mock_path)
        self.setUpPyfakefs()

    def tearDown(self):
        self.tearDownPyfakefs()

    def test_validate(self):
        with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
            self.validator.validate()
            self.assertIn('Validation successful!', stdout_m.getvalue())

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
            },
            {
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
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': '',
                    'puppet_modules': 'yy',
                    'retries': 1,
                },
                'stage': 'pre_deployment',
                'role': '*'
            }
        ]
        for data in data_sets:
            self._replace_yaml_file('tasks.yaml', data)

            with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
                self.assertFalse(self.validator.validate())
                self.assertIn('VALIDATION FAILED!', stdout_m.getvalue())

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
                {
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
            self._replace_yaml_file('tasks.yaml', data)
            with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
                self.assertTrue(self.validator.validate())
                self.assertIn('Validation successful!', stdout_m.getvalue())

    def test_check_tasks_no_file(self):
        self.fs.RemoveObject(self._make_absolute_path('tasks.yaml'))
        self.assertFalse(self.validator.validate())

    def test_check_compatibility_failed(self):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0']),
            (['6.1', '7.0', '8.0']),
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0']),
        )

        for fuel_version in fuel_version_checks:
            metadata = self._make_metadata(
                fuel_version=fuel_version,
                package_version='4.0.0')
            self._replace_yaml_file('metadata.yaml', metadata)

            err_msg = 'Current plugin format 4.0.0 is not compatible with ' \
                      '{0} Fuel release. Fuel version must be 8.0 or higher.' \
                      ' Please remove {0} version from metadata.yaml file or' \
                      ' downgrade package_version.'.format(fuel_version[0])

            with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
                self.assertFalse(self.validator.validate())
                self.assertIn(err_msg, stdout_m.getvalue())

    def test_check_compatibility_passed(self):
        metadata = self._make_metadata(
                fuel_version=['8.0'],
                package_version='4.0.0')
        self._replace_yaml_file('metadata.yaml', metadata)
        self.assertTrue(self.validator.validate())

    def test_role_attribute_is_required_for_deployment_task_types(self):
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

        err_msg = "ERROR: 'role' is a required property"
        for task in deployment_tasks_data:
            self._replace_yaml_file('deployment_tasks.yaml', [task])
            with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
                self.assertFalse(self.validator.validate())
                self.assertIn(err_msg, stdout_m.getvalue())

    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_parameters_attribute_is_required_for_deployment_task_types(
    #         self, utils_mock, *args):
    #     deployment_task_types = ['copy_files', 'sync', 'upload_file']
    #
    #     for task_type in deployment_task_types:
    #         mock_data = [{
    #             'id': 'plugin_name',
    #             'type': task_type,
    #             'role': '*'}]
    #         err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #                   "'parameters' is a required property, value path '0'"
    #         self.check_raised_exception(
    #             utils_mock, mock_data,
    #             err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_files_attribute_is_required_for_copy_files_task_type(
    #         self, utils_mock, *args):
    #     mock_data = [{
    #         'id': 'plugin_name',
    #         'type': 'copy_files',
    #         'role': '*',
    #         'parameters': {}}]
    #     err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #               "'files' is a required property, value path '0 " \
    #               "-> parameters'"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_files_should_contain_at_least_one_item_for_copy_files_task_type(
    #         self, utils_mock, *args):
    #     mock_data = [{
    #         'id': 'plugin_name',
    #         'type': 'copy_files',
    #         'role': '*',
    #         'parameters': {'files': []}}]
    #     err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #               "\[\] is too short, value path '0 -> parameters -> files'"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_src_and_dst_attributes_are_required_for_copy_files_task_type(
    #         self, utils_mock, *args):
    #     data_to_check = [
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'copy_files',
    #             'role': '*',
    #             'parameters': {
    #                 'files': [{}]}
    #         }], 'src'),
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'copy_files',
    #             'role': '*',
    #             'parameters': {
    #                 'files': [{'src': 'some_source'}]}
    #         }], 'dst')]
    #
    #     for mock_data, key in data_to_check:
    #         err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #                   "'{0}' is a required property, value path '0 " \
    #                   "-> parameters -> files -> 0'".format(key)
    #         self.check_raised_exception(
    #             utils_mock, mock_data,
    #             err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_src_and_dst_attributes_are_required_for_sync_task_type(
    #         self, utils_mock, *args):
    #     data_to_check = [
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'sync',
    #             'role': '*',
    #             'parameters': {}
    #         }], 'src'),
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'sync',
    #             'role': '*',
    #             'parameters': {'src': 'some_source'}
    #         }], 'dst')]
    #
    #     for mock_data, key in data_to_check:
    #         err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #                   "'{0}' is a required property, value path '0 " \
    #                   "-> parameters'".format(key)
    #         self.check_raised_exception(
    #             utils_mock, mock_data,
    #             err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_path_and_data_attributes_are_required_for_upload_file_task_type(
    #         self, utils_mock, *args):
    #     data_to_check = [
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'upload_file',
    #             'role': '*',
    #             'parameters': {}
    #         }], 'path'),
    #         ([{
    #             'id': 'plugin_name',
    #             'type': 'upload_file',
    #             'role': '*',
    #             'parameters': {'path': 'some_path'}
    #         }], 'data')]
    #
    #     for mock_data, key in data_to_check:
    #         err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml', " \
    #                   "'{0}' is a required property, value path '0 " \
    #                   "-> parameters'".format(key)
    #         self.check_raised_exception(
    #             utils_mock, mock_data,
    #             err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_check_group_type_deployment_task_does_not_contain_manifests(
    #         self, utils_mock, *args):
    #     utils_mock.parse_yaml.return_value = [{
    #         'id': 'plugin_name',
    #         'type': 'group',
    #         'role': ['plugin_name'],
    #         'parameters': {}}]
    #
    #     self.validator.check_deployment_tasks()
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_check_deployment_task_role_failed(self, utils_mock, *args):
    #     mock_data = [{
    #         'id': 'plugin_name',
    #         'type': 'group',
    #         'role': ['plugin_n@me']}]
    #     err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml'," \
    #               " 'plugin_n@me' does not match"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_deployment_tasks)
    #
    # @mock.patch('fuel_plugin_builder.validators.validator_v3.utils')
    # def test_check_deployment_task_role(self, utils_mock, *args):
    #     utils_mock.parse_yaml.return_value = [
    #         {'id': 'plugin_name', 'type': 'group', 'role': []},
    #         {'id': 'plugin_name', 'type': 'group', 'role': ['a', 'b']},
    #         {'id': 'plugin_name', 'type': 'group', 'role': '*'},
    #         {'id': 'plugin_name', 'type': 'puppet', 'role': []},
    #         {'id': 'plugin_name', 'type': 'puppet', 'role': ['a', 'b']},
    #         {'id': 'plugin_name', 'type': 'puppet', 'role': '*'},
    #         {'id': 'plugin_name', 'type': 'shell', 'role': []},
    #         {'id': 'plugin_name', 'type': 'shell', 'role': ['a', 'b']},
    #         {'id': 'plugin_name', 'type': 'shell', 'role': '*'},
    #         {'id': 'plugin_name', 'type': 'skipped'},
    #         {'id': 'plugin_name', 'type': 'stage'},
    #         {'id': 'plugin_name', 'type': 'reboot'},
    #         {
    #             'id': 'plugin_name',
    #             'type': 'copy_files',
    #             'role': '*',
    #             'parameters': {
    #                 'files': [
    #                     {'src': 'some_source', 'dst': 'some_destination'}]}
    #         },
    #         {
    #             'id': 'plugin_name',
    #             'type': 'sync',
    #             'role': '*',
    #             'parameters': {
    #                 'src': 'some_source', 'dst': 'some_destination'}
    #         },
    #         {
    #             'id': 'plugin_name',
    #             'type': 'upload_file',
    #             'role': '*',
    #             'parameters': {
    #                 'path': 'some_path', 'data': 'some_data'}
    #         },
    #     ]
    #
    #     self.validator.check_deployment_tasks()
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_deployment_task_id(self, utils_mock):
    #     mock_data = [{
    #         'id': 'plugin_n@me',
    #         'type': 'group',
    #         'role': ['plugin_name']}]
    #     err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml'," \
    #               " 'plugin_n@me' does not match"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_deployment_tasks_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_deployment_task_valid_dependencies(self, utils_mock):
    #     utils_mock.parse_yaml.return_value = [{
    #         'id': 'plugin_name',
    #         'type': 'group',
    #         'role': ['plugin_name'],
    #         'requires': ['dependency_1', 'dependency_2']}]
    #
    #     self.validator.check_deployment_tasks_schema()
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_deployment_task_invalid_dependencies(self, utils_mock):
    #     mock_data = [{
    #         'id': 'plugin_name',
    #         'type': 'group',
    #         'role': ['plugin_name'],
    #         'requires': ['dependency_1', 'dependency_#']}]
    #     err_msg = "File '/tmp/plugin_path/deployment_tasks.yaml'," \
    #               " 'dependency_#' does not match"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_deployment_tasks_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_node_roles_have_correct_name(self, utils_mock):
    #     mock_data = {
    #         'plug$n_n@me': {
    #             'name': 'test_plugin',
    #             'description': 'test plugin'}}
    #     err_msg = "File '/tmp/plugin_path/node_roles.yaml', Additional" \
    #               " properties are not allowed"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_node_roles_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_node_role_should_has_name(self, utils_mock):
    #     mock_data = {
    #         'plugin_name': {
    #             'description': 'test plugin'}}
    #     err_msg = "File '/tmp/plugin_path/node_roles.yaml', 'name' is" \
    #               " a required property, value path 'plugin_name'"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_node_roles_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_valid_volumes_roles_mapping_name(self, utils_mock):
    #     utils_mock.parse_yaml.return_value = {
    #         'volumes_roles_mapping': {
    #             'mapping_name': [{'allocate_size': 'min', 'id': 'test'}]},
    #         'volumes': []}
    #
    #     self.validator.check_volumes_schema()
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_invalid_volumes_roles_mapping_name(self, utils_mock):
    #     mock_data = {
    #         'volumes_roles_mapping': {
    #             'm@pping_name': [{'allocate_size': 'min', 'id': 'test'}]},
    #         'volumes': []}
    #     err_msg = "File '/tmp/plugin_path/volumes.yaml', Additional" \
    #               " properties are not allowed"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_volumes_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_valid_network_roles(self, utils_mock):
    #     utils_mock.parse_yaml.return_value = [{
    #         "id": "example_net_role",
    #         "default_mapping": "public",
    #         "properties": {
    #             "subnet": True,
    #             "gateway": False,
    #             "vip": [{
    #                 "name": "vip_name",
    #                 "namespace": "haproxy"}]}}]
    #
    #     self.validator.check_network_roles_schema()
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_network_roles_vip_have_invalid_name(self, utils_mock):
    #     mock_data = [{
    #         "id": "example_net_role",
    #         "default_mapping": "public",
    #         "properties": {
    #             "subnet": True,
    #             "gateway": False,
    #             "vip": [{
    #                 "name": "vip@name",
    #                 "namespace": "haproxy"}]}}]
    #     err_msg = "File '/tmp/plugin_path/network_roles.yaml'," \
    #               " 'vip@name' does not match"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_network_roles_schema)
    #
    # @mock.patch('fuel_plugin_builder.validators.base.utils')
    # def test_check_network_roles_vip_have_invalid_namespace(self, utils_mock):
    #     mock_data = [{
    #         "id": "example_net_role",
    #         "default_mapping": "public",
    #         "properties": {
    #             "subnet": True,
    #             "gateway": False,
    #             "vip": [{
    #                 "name": "vip_name",
    #                 "namespace": "hap roxy"}]}}]
    #     err_msg = "File '/tmp/plugin_path/network_roles.yaml'," \
    #               " 'hap roxy' does not match"
    #     self.check_raised_exception(
    #         utils_mock, mock_data,
    #         err_msg, self.validator.check_network_roles_schema)
