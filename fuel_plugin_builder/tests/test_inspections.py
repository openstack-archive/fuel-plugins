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

from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.base import Inspection
from fuel_plugin_builder.validators.checks import JSONSchemaIsValid


class TestInspections(BaseTestCase):

    @mock.patch('fuel_plugin_builder.validators.checks.utils.parse_yaml')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.exists')
    @mock.patch('fuel_plugin_builder.validators.checks.utils.isfile')
    @mock.patch('fuel_plugin_builder.utils.files_in_path')
    def test_json_schema_is_valid(
            self, files_in_path_m, isfile_m, exists_m, parse_yaml_m):
        inspection = Inspection(
            name='testInspection',
            path='/path/',
            checks=[
                JSONSchemaIsValid(
                    utils.make_schema(['data'], {'data': {'type': 'string'}})),
            ]
        )
        expected_report_text = """> Inspection: testInspection
    /path/
  > /path/file1.yaml
      > ERROR: 'data' is a required property
  > /path/file2.yaml
      > ERROR: 'data' is a required property
  > /path/file3.yaml
      > data
          > ERROR: 1 is not of type 'string'
      > data
          > ERROR: 1 is not of type 'string'"""

        files_in_path_m.return_value = [
            '/path/file1.yaml',
            '/path/file2.yaml',
            '/path/file3.yaml',  # double file3 checking path grouping
            '/path/file3.yaml'
        ]
        isfile_m.return_value = True
        exists_m.return_value = True
        parse_yaml_m.side_effect = [
            {'nosuchkey1': 'sdagasgd'},
            {'nosuchkey2': 'sdagasgd'},
            {'data': 1},
            {'data': 1}
        ]

        result = inspection.check()

        failures_count = result.count_failures()
        self.assertEqual(failures_count, 4)
        self.assertEqual(expected_report_text, result.render())
