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
import copy

import mock
from pyfakefs import fake_filesystem_unittest
import six
import yaml

from fuel_plugin_builder import consts
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder.validators.validator_v5 import ValidatorV5


class BaseValidatorTestCase(fake_filesystem_unittest.TestCase):
    example_path = None
    ValidatorClass = BaseValidator
    validator = None

    def _delete_from_fakefs(self, path):
        """Remove record from mockfs if exists.

        :param path: path
        :type path: str
        """
        fakefs_path = self._make_fakefs_path(path)
        if os.path.exists(fakefs_path):
            self.fs.RemoveObject(fakefs_path)

    def _make_fakefs_path(self, relative_path):
        """Make absolute path related to the plugin example root folder.

        :param relative_path: relative path
        :type relative_path: str
        :return: absolute path
        :rtype: str
        """
        return os.path.abspath(os.path.join(
            self.example_path, relative_path
        ))

    def _make_metadata(self, **kwargs):
        """Generate metadata based on example and custom fields from kwargs.

        :return: metadata
        :rtype: dict
        """
        metadata = copy.deepcopy({
            'package_version': '5.0.0',
            'fuel_versions': '9.1'
        })
        metadata.update(kwargs)
        return metadata

    def _update_fakefs_data(self, path, new_data):
        """Replace file with new one inside file system mock.

        :param path: relative path
        :type path: str
        :param new_data: list/dict structure that will be serialised to YAML
        :type new_data: dict|list
        """
        self._delete_from_fakefs(path)
        self.fs.CreateFile(
            self._make_fakefs_path(path),
            contents=yaml.dump(new_data)
        )

    def setUp(self):
        super(BaseValidatorTestCase, self).setUp()

        self.validator = self.ValidatorClass(self.example_path)
        for root, _, file_names in os.walk(self.example_path):
            for filename in file_names:
                local_file_path = os.path.abspath(os.path.join(root, filename))
                fakefs_path = self._make_fakefs_path(local_file_path)

                extension = utils.get_path_extension(local_file_path)
                if extension == consts.TEMPLATE_EXTENSION:
                    content = utils.template.render_template_file(
                        local_file_path, plugin_name="test-plugin")
                    fakefs_path = utils.fs.get_path_without_extension(
                        fakefs_path)

                    print ("Rendering template\n{} to\n{}".format(
                        local_file_path,
                        fakefs_path
                    ))
                else:
                    with open(local_file_path) as f:
                        content = f.read()

                self.fs.CreateFile(
                    fakefs_path,
                    content)
        # At the end to avoid importing files from mock to mock.
        self.setUpPyfakefs()

    def tearDown(self):
        self.tearDownPyfakefs()


class ValidatorV5TestCase(BaseValidatorTestCase):
    example_path = os.path.abspath('../templates/v5/plugin_data')
    ValidatorClass = ValidatorV5

    def test_validate(self):
        self._update_fakefs_data(
            'metadata.yaml',
            {'package_version': '5.0.0', 'fuel_versions': '9.1'}
        )
        report = self.validator.validate()
        self.assertIn('Validation successful!', report.render())

    def test_check_compatibility_failed(self):
        fuel_version_checks = (
            ['6.0', '6.1', '7.0', '8.0', '9.0'],
            ['6.0', '6.1', '7.0', '8.0'],
            ['6.1', '7.0', '8.0'],
            ['6.0', '6.1', '7.0'],
            ['6.1', '7.0'],
        )

        for metadata_fuel_versions in fuel_version_checks:
            metadata = self._make_metadata(
                fuel_version=metadata_fuel_versions,
                package_version=self.validator.package_version)

            self._update_fakefs_data(
                'metadata.yaml',
                metadata
            )

            report = self.validator.validate()
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
            metadata = self._make_metadata(
                fuel_version=fuel_version,
                package_version=self.validator.package_version)

            self._update_fakefs_data(
                'metadata.yaml',
                metadata
            )

            report = self.validator.validate()
            self.assertIn('Validation successful', report.render())
            self.assertEqual(report.count_failures(), 0)

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
            self._update_fakefs_data('tasks.yaml', data)
            report = self.validator.validate()
            self.assertEqual(report.count_failures(), len(data_sets))
            self.assertIn('Validation failed!', report.render())

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
            self._update_fakefs_data('tasks.yaml', data)
            with mock.patch('sys.stdout', new=six.moves.cStringIO()) as stdout_m:
                self.assertTrue(self.validator.validate())
                self.assertIn('Validation successful!', stdout_m.getvalue())

    def test_check_tasks_no_file(self):
        self._delete_from_fakefs('./tasks.yaml')
        report = self.validator.validate()
        print report.render()
        self.assertFalse(report.count_failures())

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
            self._update_fakefs_data('deployment_tasks.yaml', [task])
            report = self.validator.validate()
            self.assertFalse(report.count_failures())
            self.assertIn(err_msg, report.render())
