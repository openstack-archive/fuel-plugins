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

from fuel_plugin_builder import loaders
from fuel_plugin_builder.tests.base import FakeFSTest
from fuel_plugin_builder import validators


class TestValidatorV2(FakeFSTest):
    __test__ = True
    validator_class = validators.ValidatorV2
    loader_class = loaders.PluginLoaderV1
    package_version = '2.0.0'

    def test_check_compatibility_failed(self):
        self.data_tree['fuel_version'] = ['6.0', '6.1']
        self.data_tree['package_version'] = '2.0.0'

        err_msg = 'Current plugin format 2.0.0 is not compatible with 6.0 ' \
                  'Fuel release. Fuel version must be 6.1 or higher. ' \
                  'Please remove 6.0 version from metadata.yaml file or ' \
                  'downgrade package_version.'
        report = self.validator.validate(self.data_tree)
        self.assertTrue(report.is_failed())
        self.assertIn(err_msg, report.render())

    def test_check_tasks_not_failed(self):
        self.data_tree['tasks'] = [
            {
                'type': 'puppet',
                'role': '*',
                'stage': 'pre_deployment',
                'parameters': {
                    'timeout': 42,
                    'puppet_manifest': '/my/manifest',
                    'puppet_modules': '/my/modules'
                }
            },
            {
                'type': 'shell',
                'role': '*',
                'stage': 'pre_deployment',
                'parameters': {
                    'cmd': 'echo all > /tmp/plugin.all',
                    'timeout': 42
                }
            },
            {
                'type': 'reboot',
                'role': '*',
                'stage': 'pre_deployment',
                'parameters': {'timeout': 42}
            },
            {
                'type': 'reboot',
                'role': '*',
                'stage': 'pre_deployment/+100.1',
                'parameters': {'timeout': 42}
            },
            {
                'type': 'reboot',
                'role': '*',
                'stage': 'pre_deployment/+100',
                'parameters': {'timeout': 42}
            },
            {
                'type': 'reboot',
                'role': '*',
                'stage': 'pre_deployment/-100',
                'parameters': {'timeout': 42}
            }
        ]

        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())

    def test_check_tasks_empty_parameters_not_failed(self):
        mocked_methods = [
            'validate_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.data_tree['tasks'] = [
            {
                'type': 'reboot',
                'role': '*',
                'stage': 'pre_deployment'
            }
        ]
        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())
