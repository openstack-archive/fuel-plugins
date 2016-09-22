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

from fuel_plugin_builder import loaders
from fuel_plugin_builder.tests.base import FakeFSTest
from fuel_plugin_builder import utils
from fuel_plugin_builder import validators


class TestValidatorV1(FakeFSTest):
    validator_class = validators.ValidatorV1
    loader_class = loaders.PluginLoaderV1
    package_version = '1.0.0'

    __test__ = True

    @mock.patch('fuel_plugin_builder.validators.validator_v1'
                '.checks.multi_json_schema_is_valid')
    def test_check_schemas(self, multi_json_schema_is_valid_m):
        multi_json_schema_is_valid_m.return_value = \
            utils.ReportNode('Schema checked')
        report = self.validator.validate(self.data_tree)
        self.assertEqual(1, multi_json_schema_is_valid_m.call_count)
        self.assertIn('metadata', report.render())
        self.assertIn('tasks', report.render())
        self.assertIn('attributes', report.render())

    def test_check_env_config_attrs_checks_metadata(self):
        self.data_tree['environment_config'] = {
            'attributes': {'metadata': []}
        }
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("[] is not of type 'object'", report.render())

    def test_check_env_config_attrs_do_not_fail_if_empty(self):
        self.data_tree['environment_config'] = {}
        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())

    def test_check_env_config_attrs_fail_if_none(self):
        self.data_tree['environment_config'] = {
            'attributes': None
        }
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("None is not of type 'object'", report.render())

    def test_check_env_config_attrs_checks_attrs(self):
        self.data_tree['environment_config'] = {
            'attributes': {
                'key1': {
                    'type': True,
                    'label': 'text',
                    'value': 'text',
                    'weight': 1}}}

        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("True is not of type 'string'", report.render())

    def test_check_env_config_attrs_generator_value(self):
        self.data_tree['environment_config'] = {
            'attributes': {
                'key1': {
                    'type': 'hidden',
                    'label': '',
                    'value': {'generator': 'password'},
                    'weight': 1}}}
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("{'generator': 'password'} is not "
                      "of type 'string', 'boolean'", report.render())

    def test_check_env_config_attrs_restriction_fails(self):
        self.data_tree['environment_config'] = {
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
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("True is not of type 'string'", report.render())

    def test_check_validate(self):
        self.mock_methods(self.validator, ['validate'])
        self.validator.validate(self.data_tree)
        self.validator.validate.assert_called_once_with(self.data_tree)

    def test_check_tasks(self):
        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())

    def test_check_tasks_with_no_parameters_failed(self):
        self.data_tree['tasks'] = [{'type': 'puppet'}]
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn("'parameters' is a required property", report.render())
        self.assertIn("'stage' is a required property", report.render())
        self.assertIn("'role' is a required property", report.render())
