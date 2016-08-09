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

from fuel_plugin_builder import checks
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder import utils


class TestChecks(BaseTestCase):
    def test_json_schema_is_valid(self):
        report = checks.json_schema_is_valid(
            utils.make_schema(
                ['data'],
                {'data': {'type': 'string'}}
            ),
            {'data': 'data'}
        )
        self.assertEqual(0, report.count_failures())

    def test_json_schema_is_invalid(self):
        report = checks.json_schema_is_valid(
            utils.make_schema(
                ['data'],
                {'data': {'type': 'string'}}
            ),
            {'bad_data': 'data'}
        )
        self.assertEqual(1, report.count_failures())
        self.assertTrue(report.is_failed())
        self.assertIn("'data' is a required property", report.render())

    def test_multi_json_schema_is_valid(self):
        report = checks.multi_json_schema_is_valid(
            schemas={
                'type1': utils.make_schema(
                    ['data1'],
                    {'data1': {'type': 'string'}}
                ),
                'type2': utils.make_schema(
                    ['data2'],
                    {'data2': {'type': 'string'}}
                )
            },
            data=[
                {'type': 'type1', 'data1': 'somedata'},
                {'type': 'type2', 'data2': 'somedata'}
            ]
        )
        self.assertIn("Success!", report.render())
        self.assertFalse(report.is_failed())
        self.assertEqual(0, report.count_failures())

    def test_multi_json_schema_is_invalid(self):
        report = checks.multi_json_schema_is_valid(
            schemas={
                'type1': utils.make_schema(
                    ['data1'],
                    {'data1': {'type': 'string'}}
                ),
                'type2': utils.make_schema(
                    ['data2'],
                    {'data2': {'type': 'string'}}
                )
            },
            data=[
                {
                    'type': 'badtype',
                    'data1': 'somedata'
                },
                {
                    'type': 'type1',
                    'badkey': 'somedata'
                }

            ]
        )
        self.assertTrue(report.is_failed())
        self.assertEqual(2, report.count_failures())
        self.assertIn("Please fix 2 errors listed above", report.render())

    @mock.patch('fuel_plugin_builder.utils.fs.os.path.lexists')
    @mock.patch('fuel_plugin_builder.utils.fs.os.path.isfile')
    def test_is_file_is_ok(self, isfile_m, exists_m):
        exists_m.return_value = True
        isfile_m.return_value = True
        report = checks.file_exists('.')
        self.assertFalse(report.is_failed())

    @mock.patch('fuel_plugin_builder.utils.fs.os.path.lexists')
    @mock.patch('fuel_plugin_builder.utils.fs.os.path.isfile')
    def test_is_file_is_not_ok(self, exists_m, isfile_m):
        exists_m.return_value = True
        isfile_m.return_value = False
        report = checks.file_exists('.')
        self.assertTrue(report.is_failed())

        exists_m.return_value = False
        isfile_m.return_value = True
        report = checks.file_exists('.')
        self.assertTrue(report.is_failed())

        exists_m.return_value = False
        isfile_m.return_value = False
        report = checks.file_exists('.')
        self.assertTrue(report.is_failed())

    def test_is_compatible_ok(self):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0']),
            (['6.1', '7.0', '8.0']),
        )

        for fuel_version in fuel_version_checks:
            report = checks.fuel_ver_compatible_with_package_ver(
                minimal_fuel_version='6.0',
                plugin_metadata={
                    'fuel_version': fuel_version,
                    'package_version': '4.0.0'
                }
            )
            self.assertFalse(report.is_failed())
            self.assertIn('Expected Fuel version >= 6.0', report.render())

    def test_is_compatible_fail(self):
        fuel_version_checks = (
            (['6.0', '6.1', '7.0', '8.0', '9.0'], ['6.0', '6.1', '7.0']),
            (['6.1', '7.0'], ['6.1', '7.0']),
        )
        minimal_fuel_version = '8.0'

        for fuel_version, bad_versions, in fuel_version_checks:
            report = checks.fuel_ver_compatible_with_package_ver(
                minimal_fuel_version=minimal_fuel_version,
                plugin_metadata={
                    'fuel_version': fuel_version,
                    'package_version': '4.0.0'
                }
            )

            self.assertEqual(1, report.count_failures())
            self.assertIn(
                'Current plugin format 4.0.0 is not compatible '
                'with following Fuel versions: {0}'
                ''.format(', '.join(bad_versions)),
                report.render()
            )
            self.assertIn(
                'Fuel version must be {} or higher'
                ''.format(minimal_fuel_version),
                report.render()
            )
