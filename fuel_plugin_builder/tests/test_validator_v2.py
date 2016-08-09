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
import os

from fuel_plugin_builder.validators.validator_v2 import ValidatorV2
from tests.test_validator_base import BaseValidatorTestCase


class TestValidatorV2(BaseValidatorTestCase):

    __test__ = True
    validator_class = ValidatorV2

    plugin_path = os.path.abspath('./templates/v2/plugin_data')

    def test_check_tasks(self):
        self.data_tree['tasks'] = [
            {'type': 'puppet', 'parameters': 'param1'},
            {'type': 'shell', 'parameters': 'param2'},
            {'type': 'reboot', 'parameters': 'param3'}]

        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())

    def test_check_tasks_no_parameters_not_failed(self):
        mocked_methods = [
            'validate_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.data_tree['tasks'] = [
            {'type': 'puppet'},
        ]
        report = self.validator.validate(self.data_tree)
        self.assertFalse(report.is_failed())