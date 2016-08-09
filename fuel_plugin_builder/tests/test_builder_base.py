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

from __future__ import unicode_literals

from os.path import join as join_path

import mock

from fuel_plugin_builder import utils
from fuel_plugin_builder.builders import BuilderBase
from fuel_plugin_builder.tests.base import BaseTestCase


class BaseBuildTestCase(BaseTestCase):
    # Prevent test runner to run tests in base
    __test__ = False
    # Redefine class
    builder_class = BuilderBase
    fake_metadata = None

    releases = [
        {'os': 'ubuntu',
         'deployment_scripts_path': 'deployment_scripts_path',
         'repository_path': 'repository_path'}]

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.plugin_path = '/tmp/fuel_plugin'
        self.builder = self._create_builder(self.plugin_path)

    def _create_builder(self, plugin_path, fake_metadata=None):
        fake_metadata = utils.ReportNode().mix_to_data(
            fake_metadata or self.fake_metadata)
        loader = self.builder_class.loader_class(plugin_path)
        loader.load = mock.Mock(return_value=fake_metadata)
        return self.builder_class(plugin_path, loader=loader)

    def test_run(self):
        mocked_methods = [
            'clean',
            'run_pre_build_hook',
            'check',
            'build_repos',
            'add_checksums_file',
            'make_package']

        self.mock_methods(self.builder, mocked_methods)
        self.builder.run()

        self.builder.clean.assert_called_once_with()
        self.builder.run_pre_build_hook.assert_called_once_with()
        self.builder.check.assert_called_once_with()
        self.builder.add_checksums_file()
        self.builder.build_repos.assert_called_once_with()
        self.builder.make_package()

    @mock.patch('fuel_plugin_builder.utils.which')
    @mock.patch('fuel_plugin_builder.utils.exec_cmd',
                return_value=True)
    def test_run_pre_build_hook(self, exec_cmd_mock, which_mock):
        self.builder.run_pre_build_hook()
        exec_cmd_mock.assert_called_once_with(self.builder.pre_build_hook_cmd,
                                              self.builder.plugin_path)
        which_mock.assert_called_once_with(
            join_path(self.builder.plugin_path,
                      self.builder.pre_build_hook_cmd))

    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.copy_files_in_dir')
    def test_build_repos(self, copy_files_in_dir_m, create_dir_m):
        with mock.patch.object(
                self.builder_class, 'build_ubuntu_repos') as build_ubuntu_mock:
            with mock.patch.object(
                    self.builder_class,
                    'build_centos_repos') as build_centos_mock:
                self.builder.build_repos()

            create_dir_m.assert_called_once_with(
                self.builder.build_src_dir)
            copy_files_in_dir_m.assert_called_once_with(
                '/tmp/fuel_plugin/*',
                self.builder.build_src_dir)
            build_centos_mock.assert_called_once_with([])
            build_ubuntu_mock.assert_called_once_with([
                '/tmp/fuel_plugin/.build/src/repository_path'])

    @mock.patch('fuel_plugin_builder.utils.exec_piped_cmds')
    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    def test_build_ubuntu_repos(self,
                                load_template_and_render_to_file_m,
                                exec_piped_cmds_m):
        path = '/repo/path'
        self.builder.build_ubuntu_repos([path])
        exec_piped_cmds_m.assert_called_once_with(
            ['dpkg-scanpackages -m .', 'gzip -c9 > Packages.gz'],
            cwd=path)

    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.move_files_in_dir')
    @mock.patch('fuel_plugin_builder.utils.exec_cmd')
    def test_build_centos_repos(
            self, exec_cmd_m, move_files_in_dir_m, create_dir_m):
        path = '/repo/path'
        self.builder.build_centos_repos([path])
        create_dir_m.assert_called_once_with(
            '/repo/path/Packages')
        move_files_in_dir_m.assert_called_once_with(
            '/repo/path/*.rpm', '/repo/path/Packages')
        exec_cmd_m.assert_called_once_with(
            'createrepo -o /repo/path /repo/path')

    @mock.patch.object(BuilderBase, '_check_requirements')
    @mock.patch.object(BuilderBase, '_validate')
    def test_check(self, check_structure_mock, check_requirements_mock):
        self.builder.check()
        check_structure_mock.assert_called_once_with()
        check_requirements_mock.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.utils.which',
                return_value=True)
    def test_check_requirements(self, _):
        self.builder._check_requirements()

    @mock.patch('fuel_plugin_builder.version_mapping.get_validator')
    def test_check_structure(self, get_validator_m):
        validator_mock = mock.MagicMock()
        get_validator_m.return_value = validator_mock

        self.builder._validate()

        get_validator_m.assert_called_once_with(self.plugin_path)
        validator_mock.validate.assert_called_once_with()

    @mock.patch(
        'fuel_plugin_builder.utils.create_checksums_file')
    def test_add_checksums_file(self, create_checksums_file_mock):
        self.builder.add_checksums_file()
        create_checksums_file_mock.assert_called_once_with(
            self.builder.build_src_dir, self.builder.checksums_path)

    @mock.patch('fuel_plugin_builder.utils.remove')
    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.remove_by_mask')
    def test_clean(self, remove_by_mask_m, created_dir_m, remove_m):
        self.builder.clean()
        remove_m.assert_called_once_with(self.builder.build_dir),
        created_dir_m.assert_called_once_with(self.builder.build_dir),
        remove_by_mask_m.assert_called_once_with(
            self.builder.result_package_mask)
