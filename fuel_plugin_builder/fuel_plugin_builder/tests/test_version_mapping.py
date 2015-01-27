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

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.validators import ValidatorV1
from fuel_plugin_builder.validators import ValidatorV2
from fuel_plugin_builder.version_mapping import get_plugin_for_version


class TestVersionMapping(BaseTestCase):

    def test_get_plugin_for_version_1(self):
        result = get_plugin_for_version('1.0.0')
        self.assertEqual(result['version'], '1.0.0')
        self.assertEqual(
            result['templates'],
            ['templates/base', 'templates/v1/'])
        self.assertEqual(result['validator'], ValidatorV1)

    def test_get_plugin_for_version_2(self):
        result = get_plugin_for_version('2.0.0')
        self.assertEqual(result['version'], '2.0.0')
        self.assertEqual(
            result['templates'],
            ['templates/base', 'templates/v2/'])
        self.assertEqual(result['validator'], ValidatorV2)

    def test_get_plugin_for_version_raises_error(self):
        with self.assertRaisesRegexp(errors.WrongPackageVersionError,
                                     'Wrong package version "2999"'):
            get_plugin_for_version('2999')
