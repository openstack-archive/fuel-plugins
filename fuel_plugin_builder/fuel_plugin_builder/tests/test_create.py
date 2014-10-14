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

from fuel_plugin_builder.actions import CreatePlugin
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase


class TestCreate(BaseTestCase):

    def setUp(self):
        self.plugins_name = 'fuel_plugin'
        self.plugin_path = '/tmp/{0}'.format(self.plugins_name)
        self.template_dir = '/temp_dir'
        self.creator = CreatePlugin(self.plugin_path)
        self.creator.template_dir = self.template_dir
        self.creator.plugin_structure = [
            {'action': 'render', 'path': 'file1', 'from': 'temp_file1'},
            {'action': 'copy', 'path': 'file2', 'from': 'temp_file2'},
            {'action': 'mkdir', 'path': 'tmp'}]

    @mock.patch('fuel_plugin_builder.actions.create.utils.exists',
                return_value=False)
    def test_check(self, exists_mock):
        self.creator.check()
        exists_mock.assert_called_once_with(self.plugin_path)

    @mock.patch('fuel_plugin_builder.actions.create.utils.exists',
                return_value=True)
    def test_check_raises_errors(self, exists_mock):
        self.assertRaisesRegexp(
            errors.PluginDirectoryExistsError,
            'Plugins directory {0} already exists, '
            'choose anothe name'.format(self.plugin_path),
            self.creator.check)
        exists_mock.assert_called_once_with(self.plugin_path)

    @mock.patch('fuel_plugin_builder.actions.create.utils')
    def test_run(self, utils_mock):
        self.creator.run()
        utils_mock.render_to_file.assert_called_once_with(
            '/temp_dir/temp_file1',
            '/tmp/fuel_plugin/file1',
            self.creator.render_ctx)

        utils_mock.copy_file_permissions.assert_called_once_with(
            '/temp_dir/temp_file1',
            '/tmp/fuel_plugin/file1')

        self.assertEqual(
            utils_mock.create_dir.call_args_list,
            [mock.call('/tmp/fuel_plugin'),
             mock.call('/tmp/fuel_plugin/tmp')])

        utils_mock.copy.assert_called_once_with(
            '/temp_dir/temp_file2',
            '/tmp/fuel_plugin/file2')
