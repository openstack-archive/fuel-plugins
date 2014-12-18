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
                'fuel_plugin_builder.actions.build.utils.parse_yaml',
                return_value="line 1\n line2\n line3"):
            self.builder = BuildPlugin(self.plugin_path)

        self.releases = [
            {'os': 'ubuntu',
             'deployment_scripts_path': 'deployment_scripts_path',
             'repository_path': 'repository_path'}]

        self.builder.meta = {
            'name': 'awesome_plugin',
            'version': '2.0.1',
            'releases': self.releases}

    def test_run(self):
        mocked_methods = [
            'run_pre_build_hook',
            'check',
            'build_repos',
            'add_checksums_file',
            'make_package']

        self.mock_methods(self.builder, mocked_methods)
        self.builder.run()

        self.builder.run_pre_build_hook.assert_called_once_with()
        self.builder.check.assert_called_once_with()
        self.builder.add_checksums_file()
        self.builder.build_repos.assert_called_once_with()
        self.builder.make_package()

    @mock.patch('fuel_plugin_builder.actions.build.utils.which')
    @mock.patch('fuel_plugin_builder.actions.build.utils.exec_cmd',
                return_value=True)
    def test_run_pre_build_hook(self, exec_cmd_mock, which_mock):
        self.builder.run_pre_build_hook()
        exec_cmd_mock.assert_called_once_with(self.builder.pre_build_hook_path)
        which_mock.assert_called_once_with(self.builder.pre_build_hook_path)

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

    @mock.patch.object(BuildPlugin, 'build_ubuntu_repos')
    @mock.patch.object(BuildPlugin, 'build_centos_repos')
    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_repos(self,
                         utils_mock,
                         build_centos_mock,
                         build_ubuntu_mock):
        self.builder.build_repos()

        utils_mock.remove.assert_called_once_with(self.builder.build_dir)
        utils_mock.create_dir.assert_called_once_with(self.builder.build_dir)
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
            'dpkg-scanpackages . | gzip -c9 > Packages.gz',
            cwd=path)

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

    @mock.patch.object(BuildPlugin, '_check_requirements')
    @mock.patch.object(BuildPlugin, '_check_structure')
    def test_check(self, check_structure_mock, check_requirements_mock):
        self.builder.check()
        check_structure_mock.assert_called_once_with()
        check_requirements_mock.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpm, createrepo, dpkg-scanpackages", '
            'install required commands and try again',
            self.builder._check_requirements)

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=True)
    def test_check_requirements(self, _):
        self.builder._check_requirements()

    @mock.patch('fuel_plugin_builder.actions.build.ValidatorManager')
    def test_check_structure(self, manager_class_mock):
        validator_manager_obj = mock.MagicMock()
        manager_class_mock.return_value = validator_manager_obj
        validator_mock = mock.MagicMock()
        validator_manager_obj.get_validator.return_value = validator_mock

        self.builder._check_structure()

        manager_class_mock.assert_called_once_with(self.plugin_path)
        validator_manager_obj.get_validator.assert_called_once_with()
        validator_mock.validate.assert_called_once_with()

    @mock.patch(
        'fuel_plugin_builder.actions.build.utils.create_checksums_file')
    def test_add_checksums_file(self, create_checksums_file_mock):
        self.builder.add_checksums_file()
        create_checksums_file_mock.assert_called_once_with(
            self.builder.build_dir, self.builder.checksums_path)
