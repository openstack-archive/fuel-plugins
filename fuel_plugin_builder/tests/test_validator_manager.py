# -*- coding: utf-8 -*-

#    Copyright 2014 Mirantis, Inc.
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
from fuel_plugin_builder.validators import ValidatorManager


class TestValidatorManager(BaseTestCase):

    def setUp(self):
        self.plugin_path = '/tmp/plugin_path'

    def test_get_validator(self):
        validator = mock.MagicMock(return_value='test')

        with mock.patch(
                'fuel_plugin_builder.validators.manager.'
                'version_mapping.get_version_mapping_from_plugin',
                return_value={'validator': validator}):
            self.assertEqual(
                ValidatorManager(self.plugin_path).get_validator(),
                'test')

        validator.assert_called_once_with(self.plugin_path)
