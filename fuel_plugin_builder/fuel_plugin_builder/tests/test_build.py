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

from fuel_plugin_builder.actions import BuildPlugin
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase


class TestBuild(BaseTestCase):

    def setUp(self):
        self.plugins_name = 'fuel_plugin'
        self.plugin_path = '/tmp/{0}'.format(self.plugins_name)

        with mock.patch(
                '__builtin__.open',
                self.mock_open("line 1\n line2\n line3")):
            self.builder = BuildPlugin(self.plugin_path)

        self.releases = [
            {'os': 'ubuntu',
             'deployment_scripts_path': 'deployment_scripts_path',
             'repository_path': 'repository_path'}]

        self.builder.meta = {
            'name': 'awesome_plugin',
            'version': '2.0.1',
            'releases': self.releases}

    @mock.patch('fuel_plugin_builder.actions.build.BuildPlugin.build_repos')
    @mock.patch('fuel_plugin_builder.actions.build.BuildPlugin.make_package')
    def test_run(self, builde_repo_mock, make_package_mock):
        self.builder.run()
        builde_repo_mock.assert_called_once_with()
        make_package_mock.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_make_package(self, utils_mock):
        utils_mock.exists.return_value = True
        self.builder.make_package()
        tar_path = '/tmp/fuel_plugin/awesome_plugin-2.0.1.fp'

        utils_mock.exists.assert_called_once_with(tar_path)
        utils_mock.remove.assert_called_once_with(tar_path)
        utils_mock.make_tar_gz.assert_called_once_with(
            self.builder.build_dir,
            tar_path,
            'awesome_plugin-2.0.1')

    @mock.patch(
        'fuel_plugin_builder.actions.build.BuildPlugin.build_ubuntu_repos')
    @mock.patch(
        'fuel_plugin_builder.actions.build.BuildPlugin.build_centos_repos')
    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_repos(self,
                         utils_mock,
                         build_centos_mock,
                         build_ubuntu_mock):
        utils_mock.which.return_value = True
        self.builder.build_repos()

        utils_mock.remove.assert_called_once_with(self.builder.build_dir)
        utils_mock.create_dir.assert_called_once_with(self.builder.build_dir)
        utils_mock.which.assert_called_once_with(
            self.builder.pre_build_hook_path)
        utils_mock.exec_cmd.assert_called_once_with(
            self.builder.pre_build_hook_path)
        utils_mock.copy_files_in_dir.assert_called_once_with(
            '/tmp/fuel_plugin/*',
            self.builder.build_dir)
        build_centos_mock.assert_called_once_with([])
        build_ubuntu_mock.assert_called_once_with([
            '/tmp/fuel_plugin/.build/repository_path'])

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_ubuntu_repos(self, utils_mock):
        path = '/repo/path'
        self.builder.build_ubuntu_repos([path])
        utils_mock.exec_cmd.assert_called_once_with(
            'dpkg-scanpackages /repo/path | gzip -c9 > /repo/path/Packages.gz')

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_centos_repos(self, utils_mock):
        path = '/repo/path'
        self.builder.build_centos_repos([path])
        utils_mock.create_dir.assert_called_once_with(
            '/repo/path/Packages')
        utils_mock.move_files_in_dir.assert_called_once_with(
            '/repo/path/*.rpm', '/repo/path/Packages')
        utils_mock.exec_cmd.assert_called_once_with(
            'createrepo -o /repo/path /repo/path')

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=True)
    def test_check(self, _):
        self.builder.check()

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=False)
    def test_check_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpm, createrepo, dpkg-scanpackages", '
            'install required commands and try again',
            self.builder.check)
