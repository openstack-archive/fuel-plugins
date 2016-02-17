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
from fuel_plugin_builder.validators.checks import JsonSchemaIsValid

try:
    from unittest.case import TestCase
except ImportError:
    # Required for python 2.6
    from unittest2.case import TestCase


class TestChecks(TestCase):
    def setUp(self):
        pass

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def test_json_schema_is_valid(self, isfile_m, exists_m, parse_yaml_m):
        check = JsonSchemaIsValid(
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
        check = JsonSchemaIsValid(
            schema=utils.make_schema(['data'], {'data': {'type': 'string'}})
        )
        exists_m.return_value = True
        isfile_m.return_value = True
        parse_yaml_m.return_value = {'no key': 'data'}

        result = check.check_file('.')
        output = result.render()
        failures_count = result.count_failures()
        self.assertEqual(failures_count, 1)
        self.assertIn("ERROR: JSON Schema validation failed, "
                      "'data' is a required property", output)

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml_file')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    def multi_json_schema_is_invalid(self, isfile_m, exists_m, parse_yaml_m):
        check = JsonSchemaIsValid(
            schema=utils.make_schema(['data'], {'data': {'type': 'string'}})
        )
        exists_m.return_value = True
        isfile_m.return_value = True
        parse_yaml_m.return_value = {'no key': 'data'}

        result = check.check_file('.')
        output = result.report.render()
        failures_count = result.count_failures()
        self.assertEqual(failures_count, 1)
        self.assertIn("ERROR: JSON Schema validation failed, "
                      "'data' is a required property", output)
