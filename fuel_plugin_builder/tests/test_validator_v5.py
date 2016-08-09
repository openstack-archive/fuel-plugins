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
import base
from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder.validators.validator_v5 import ValidatorV5


class BaseValidatorTestCase(base.FakeFSTest):
    fake_fs_source_path = None
    validator = None
    ValidatorClass = BaseValidator

    def SetUp(self):
        super(BaseValidatorTestCase, self).setUp()
        self.validator = self.ValidatorClass(self.fake_fs_source_path)


class ValidatorV5TestCase(BaseValidatorTestCase):
    example_path = os.path.abspath('../templates/v5/plugin_data')
    ValidatorClass = ValidatorV5

    def test_validate(self):
        self._patch_fakefs_file(
            'metadata.yaml',
            self._make_fake_metadata_data(
                package_version='5.0.0',
                fuel_version=['9.1']
            )
        )
        report = self.validator.validate()
        self.assertIn('Validation successful!', report.render())

    def test_check_compatibility_failed(self):
        fuel_version_checks = (
            ['6.0', '6.1', '7.0', '8.0', '9.0'],
            ['6.0', '6.1', '7.0', '8.0'],
            ['6.1', '7.0', '8.0']
        )

        for metadata_fuel_versions in fuel_version_checks:
            metadata = self._make_fake_metadata_data(
                fuel_version=metadata_fuel_versions,
                package_version=self.validator.package_version)

            self._patch_fakefs_file(
                'metadata.yaml',
                metadata
            )

            report = self.validator.validate(self.example_path)
            self.assertTrue(report.count_failures() > 0)
            self.assertIn(
                u'Current plugin format {package_version} is not compatible '
                u'with following Fuel versions: {metadata_fuel_versions}\n'
                u'Fuel version must be {minimal_fuel_version} or higher. '
                u'Please remove {metadata_fuel_versions} version from '
                u'{metadata_path} file or downgrade package_version.'.format(
                    package_version=self.validator.package_version,
                    minimal_fuel_version=self.validator.minimal_fuel_version,
                    metadata_fuel_versions=u", ".join(metadata_fuel_versions),
                    metadata_path='metadata.yaml'
                ),
                report.render()
            )

    def test_check_compatibility_passed(self):
        fuel_version_checks = (
            (['8.0', '9.0', '9.1']),
            (['8.0', '9.0', '9.1', '9.2']),
            (['8.0', '9.0', '9.1', '9.2', '10.0']),
        )

        for fuel_version in fuel_version_checks:
            metadata = self._make_fake_metadata_data(
                fuel_version=fuel_version,
                package_version=self.validator.package_version)

            self._patch_fakefs_file(
                'metadata.yaml',
                metadata
            )

            report = self.validator.validate()
            self.assertIn('Validation successful', report.render())
            self.assertEqual(report.count_failures(), 0)

    def test_check_tasks_schema_validation_failed(self):
        bad_tasks_data = [
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

        self._create_fakefs_file(
            'graphs/deployment_tasks.yaml',
            bad_tasks_data
        )
        report = self.validator.validate()
        self.assertEqual(report.count_failures(), 7 + 1)
        self.assertIn('Validation failed!', report.render())

    def test_check_tasks_schema_validation_passed(self):
        data_sets = [
            [
                {
                    'id': 'test1',
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
                    'id': 'test1',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test2',
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
                    'id': 'test3',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test4',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test5',
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
                    'id': 'test1',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test2',
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
                    'id': 'test3',
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
                    'id': 'test4',
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
            self._create_fakefs_file('graphs/deployment_tasks.yaml', data)
            report = self.validator.validate()
            self.assertFalse(report.is_failed())
            self.assertIn('Validation successful!', report.render())

    def test_no_legacy_tasks_ok(self):
        metadata = self._make_fake_metadata_data(
            fuel_version=['9.1'],
            package_version=self.validator.package_version
        )

        self._patch_fakefs_file(
            'metadata.yaml',
            metadata
        )

        self._delete_from_fakefs('./tasks.yaml')
        report = self.validator.validate()
        self.assertFalse(report.count_failures())

    def test_check_warn_on_tasks_file(self):
        metadata = self._make_fake_metadata_data()

        self._patch_fakefs_file(
            'metadata.yaml',
            metadata
        )

        self._create_fakefs_file('./tasks.yaml', [])
        report = self.validator.validate()
        self.assertFalse(report.count_failures())

    def test_more_one_release_is_not_ok(self):
        self._create_fakefs_file(
            'metadata.yaml',
            {

            }
        )

