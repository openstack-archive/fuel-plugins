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

import mock

from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.checks import DoPathHaveFiles
from fuel_plugin_builder.validators.checks import EnvConfigAttrsIsValidV1
from fuel_plugin_builder.validators.checks import IsFile
from fuel_plugin_builder.validators.checks import IsReleaseCompatible
from fuel_plugin_builder.validators.checks import JSONSchemaIsValid
from fuel_plugin_builder.validators.checks import MultiJSONSchemaIsValid
from fuel_plugin_builder.validators.checks import ScriptsAndRepoPathsIsValid

try:
    from unittest.case import TestCase
except ImportError:
    # Required for python 2.6
    from unittest2.case import TestCase


class TestChecks(TestCase):

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_json_schema_is_valid(self, isfile_m, exists_m, parse_yaml_m):
        check = JSONSchemaIsValid(
            schema=utils.make_schema(['data'], {'data': {'type': 'string'}})
        )
        isfile_m.return_value = True
        exists_m.return_value = True
        parse_yaml_m.return_value = {'data': 'data'}

        result = check.check_file('.')
        output = result.render()
        failures_count = result.count_failures()
        self.assertEqual(failures_count, 0)
        self.assertEqual(output, "")

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_json_schema_is_invalid(self, isfile_m, exists_m, parse_yaml_m):
        check = JSONSchemaIsValid(
            schema=utils.make_schema(['data'], {'data': {'type': 'string'}})
        )
        exists_m.return_value = True
        isfile_m.return_value = True
        parse_yaml_m.return_value = {'no key': 'data'}

        result = check.check_file('.')
        self.assertEqual(1, result.count_failures())
        self.assertIn("ERROR: 'data' is a required property", result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_multi_json_schema_is_valid(self,
                                        isfile_m, exists_m, parse_yaml_m):
        check = MultiJSONSchemaIsValid(
            schemas={
                'type1': utils.make_schema(
                    ['data1'],
                    {'data1': {'type': 'string'}}
                ),
                'type2': utils.make_schema(
                    ['data2'],
                    {'data2': {'type': 'string'}}
                )
            }
        )
        exists_m.return_value = True
        isfile_m.return_value = True
        parse_yaml_m.return_value = [
            {'type': 'type1', 'data1': 'somedata'},
            {'type': 'type2', 'data2': 'somedata'}
        ]

        result = check.check_file('.')
        self.assertEqual('', result.render())
        self.assertEqual(0, result.count_failures())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_multi_json_schema_is_invalid(
            self, isfile_m, exists_m, parse_yaml_m):

        data_fixtures = [
            [
                {'type': 'badtype', 'data1': 'somedata'},
            ],
            [
                {'type': 'type1', 'badkey': 'somedata'},
            ]
        ]
        check = MultiJSONSchemaIsValid(
            schemas={
                'type1': utils.make_schema(
                    ['data1'],
                    {'data1': {'type': 'string'}}
                ),
                'type2': utils.make_schema(
                    ['data2'],
                    {'data2': {'type': 'string'}}
                )
            }
        )
        exists_m.return_value = True
        isfile_m.return_value = True

        for data in data_fixtures:
            parse_yaml_m.return_value = data
            result = check.check_file('.')
            self.assertEqual(result.count_failures(), 1)
            self.assertIn('ERROR: ', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.files_in_path')
    def test_do_path_have_files_valid(self, files_in_path_m):
        files_in_path_m.return_value = ['file1', 'file2']
        check = DoPathHaveFiles()
        result = check.check_path('.')
        self.assertEqual(0, result.count_failures())
        self.assertEqual('', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.files_in_path')
    def test_do_path_have_files_invalid(self, files_in_path_m):
        files_in_path_m.return_value = []
        check = DoPathHaveFiles()
        result = check.check_path('.')
        self.assertEqual(1, result.count_failures())
        self.assertIn('ERROR: Path contain no files', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_is_file_with_required_ok(self, isfile_m, exists_m):
        check = IsFile()
        exists_m.return_value = True
        isfile_m.return_value = True
        result = check.check_path('.')
        self.assertEqual(0, result.count_failures())
        self.assertEqual('', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_is_file_with_required_fail_not_exist(self, isfile_m, exists_m):
        check = IsFile()
        exists_m.return_value = False
        isfile_m.return_value = False
        result = check.check_path('.')
        self.assertEqual(1, result.count_failures())
        self.assertIn('ERROR: File not found', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_is_file_with_required_fail_not_file(self, isfile_m, exists_m):
        check = IsFile()
        exists_m.return_value = True
        isfile_m.return_value = False
        result = check.check_path('/')
        self.assertEqual(1, result.count_failures())
        self.assertIn('ERROR: Path is not file', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_is_file_without_required_ok(self, isfile_m, exists_m):
        check = IsFile(required=False)
        result = check.check_path('badpath')
        exists_m.return_value = False
        isfile_m.return_value = False
        self.assertEqual(0, result.count_failures())
        self.assertEqual('', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_is_file_without_required_fail(self, isfile_m, exists_m):
        check = IsFile(required=False)
        exists_m.return_value = True
        isfile_m.return_value = False
        result = check.check_path('/')
        self.assertEqual(1, result.count_failures())
        self.assertIn('ERROR: Path is not file', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_is_compatible_ok(self, parse_yaml_file_m):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0']),
            (['6.1', '7.0', '8.0']),
        )
        check = IsReleaseCompatible(basic_version='6.0')

        for fuel_version in fuel_version_checks:
            parse_yaml_file_m.return_value = {
                'fuel_version': fuel_version,
                'package_version': '4.0.0'}
            result = check.check_file('metadata.yaml')

            self.assertEqual(0, result.count_failures())
            self.assertIn('INFO: Expected Fuel version >=6.0', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_is_compatible_fail(self, parse_yaml_file_m):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0', '9.0']),
            (['6.1', '7.0', '8.0']),
        )
        basic_version = '8.0'
        good_versions = ['8.0', '9.0']
        check = IsReleaseCompatible(basic_version=basic_version)

        for fuel_version in fuel_version_checks:
            invalid_fuel_versions = [
                v for v in fuel_version if v not in good_versions]
            parse_yaml_file_m.return_value = {
                'fuel_version': fuel_version,
                'package_version': '4.0.0'}
            result = check.check_file('metadata.yaml')

            self.assertEqual(
                len(invalid_fuel_versions), result.count_failures())
            for invalid_version in invalid_fuel_versions:
                err_msg = 'Current plugin format 4.0.0 is not compatible ' \
                          'with {0} Fuel release. Fuel version must be {1} ' \
                          'or higher. Please remove {0} version from ' \
                          'metadata.yaml file or downgrade package_version.' \
                          ''.format(invalid_version, basic_version)
                self.assertIn(err_msg, result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_env_scripts_and_repo_paths_ok(self, parse_yaml_file_m, exists_m):
        parse_yaml_file_m.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': 'repository_path'}]}

        exists_m.return_value = True
        check = ScriptsAndRepoPathsIsValid(base_path='.')
        check.check_file('metadata.yaml')

        self.assertEqual(
            exists_m.call_args_list,
            [mock.call('/tmp/deployment_scripts_path'),
             mock.call('./repository_path')])

    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_env_scripts_and_repo_paths_fail(self,
                                             parse_yaml_file_m, exists_m):
        parse_yaml_file_m.return_value = {
            'releases': [{
                'repository_path': 'repository_path'}]}

        exists_m.return_value = False
        check = ScriptsAndRepoPathsIsValid(base_path='.')
        result = check.check_file('metadata.yaml')
        self.assertEqual(2, result.count_failures())
        self.assertIn('ERROR: Field deployment_scripts_path not specified '
                      'for the release', result.render())
        self.assertIn('Cannot find directory ./repository_path '
                      'for the release', result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_env_config_attr_pass(self, parse_yaml_file_m):
        parse_yaml_file_m.return_value = {}

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_check_env_config_attrs_1_fail_if_none(self, parse_yaml_file_m):
        check = EnvConfigAttrsIsValidV1()
        parse_yaml_file_m.return_value = {'attributes': None}
        result = check.check_file('environment_config.yaml')

        self.assertEqual(1, result.count_failures())
        self.assertIn("ERROR: None is not of type 'object'", result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_check_env_config_attrs_checks_metadata(self, parse_yaml_file_m):
        check = EnvConfigAttrsIsValidV1()
        parse_yaml_file_m.return_value = {'attributes': {'metadata': []}}
        result = check.check_file('environment_config.yaml')

        self.assertEqual(1, result.count_failures())
        self.assertIn("ERROR: [] is not of type 'object'", result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_check_env_config_attrs_checks_attrs(self, parse_yaml_file_m):
        check = EnvConfigAttrsIsValidV1()
        parse_yaml_file_m.return_value = {
            'attributes': {
                'key1': {
                    'type': True,
                    'label': 'text',
                    'value': 'text',
                    'weight': 1}}}
        result = check.check_file('environment_config.yaml')
        self.assertEqual(1, result.count_failures())
        self.assertIn("ERROR: True is not of type 'string'", result.render())

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    def test_check_env_config_attrs_restriction_fails(self, parse_yaml_file_m):
        check = EnvConfigAttrsIsValidV1()
        parse_yaml_file_m.return_value = {
            'attributes': {
                'key1': {
                    'type': 'text',
                    'label': 'test',
                    'value': 'test',
                    'weight': 1,
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        },
                        {
                            'condition': True,
                            'action': 'hide'
                        }
                    ]
                }
            }
        }
        result = check.check_file('environment_config.yaml')
        self.assertEqual(4, result.count_failures())
        self.assertIn("attributes -> key1", result.render())
        self.assertIn("restrictions -> 1", result.render())
        self.assertIn("ERROR: True is not of type 'string'", result.render())
