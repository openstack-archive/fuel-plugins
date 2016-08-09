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

from fuel_plugin_builder import builders
from fuel_plugin_builder import loaders
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder import validators
from fuel_plugin_builder.version_mapping import \
    get_plugin_package_config


class TestVersionMapping(BaseTestCase):
    def test_get_plugin_for_existing_versions(self):
        for n, valdator, builder, loader in (
            (
                1,
                validators.ValidatorV1,
                builders.PluginBuilderV1,
                loaders.PluginLoaderV1
            ),
            (
                2,
                validators.ValidatorV2,
                builders.PluginBuilderV2,
                loaders.PluginLoaderV1
            ),
            (
                3,
                validators.ValidatorV3,
                builders.PluginBuilderV3,
                loaders.PluginLoaderV3
            ),
            (
                4,
                validators.ValidatorV4,
                builders.PluginBuilderV3,
                loaders.PluginLoaderV4
            ),
            (
                5,
                validators.ValidatorV5,
                builders.PluginBuilderV3,
                loaders.PluginLoaderV5
            )
        ):
            result = get_plugin_package_config('{}.0.0'.format(n))
            self.assertEqual(result['version'], '{}.0.'.format(n))
            self.assertEqual(result['validator'], valdator)
            self.assertEqual(result['builder'], builder)
            self.assertEqual(result['loader'], loader)

    def test_get_plugin_for_version_raises_error(self):
        with self.assertRaisesRegexp(Exception,
                                     'Wrong package version "2999"'):
            get_plugin_package_config('2999')
