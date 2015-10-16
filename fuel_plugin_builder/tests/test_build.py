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

from __future__ import unicode_literals

import mock
import os

from os.path import join as join_path

from fuel_plugin_builder.actions.build import BaseBuildPlugin
from fuel_plugin_builder.actions.build import BuildPluginV1
from fuel_plugin_builder.actions.build import BuildPluginV2
from fuel_plugin_builder.actions.build import BuildPluginV3
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase


class BaseBuild(BaseTestCase):

    # Prevent test runner to run tests in base
    __test__ = False
    # Redefine class
    builder_class = None

    releases = [
        {'os': 'ubuntu',
         'deployment_scripts_path': 'deployment_scripts_path',
         'repository_path': 'repository_path'}]

    def setUp(self):
        self.plugins_name = 'fuel_plugin'
        self.plugin_path = '/tmp/{0}'.format(self.plugins_name)
        self.builder = self.create_builder(self.plugin_path)

    def create_builder(self, plugin_path):
        with mock.patch(
                'fuel_plugin_builder.actions.build.utils.parse_yaml',
                return_value=self.meta):
            return self.builder_class(plugin_path)

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

    @mock.patch('fuel_plugin_builder.actions.build.utils.which')
    @mock.patch('fuel_plugin_builder.actions.build.utils.exec_cmd',
                return_value=True)
    def test_run_pre_build_hook(self, exec_cmd_mock, which_mock):
        self.builder.run_pre_build_hook()
        exec_cmd_mock.assert_called_once_with(self.builder.pre_build_hook_path)
        which_mock.assert_called_once_with(self.builder.pre_build_hook_path)

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_repos(self, utils_mock):
        with mock.patch.object(
                self.builder_class, 'build_ubuntu_repos') as build_ubuntu_mock:
            with mock.patch.object(
                    self.builder_class,
                    'build_centos_repos') as build_centos_mock:
                self.builder.build_repos()

        utils_mock.create_dir.assert_called_once_with(
            self.builder.build_src_dir)
        utils_mock.copy_files_in_dir.assert_called_once_with(
            '/tmp/fuel_plugin/*',
            self.builder.build_src_dir)
        build_centos_mock.assert_called_once_with([])
        build_ubuntu_mock.assert_called_once_with([
            '/tmp/fuel_plugin/.build/src/repository_path'])

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_ubuntu_repos(self, utils_mock):
        path = '/repo/path'
        self.builder.build_ubuntu_repos([path])
        utils_mock.exec_piped_cmds.assert_called_once_with(
            ['dpkg-scanpackages .', 'gzip -c9 > Packages.gz'],
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

    @mock.patch.object(BaseBuildPlugin, '_check_requirements')
    @mock.patch.object(BaseBuildPlugin, '_check_structure')
    def test_check(self, check_structure_mock, check_requirements_mock):
        self.builder.check()
        check_structure_mock.assert_called_once_with()
        check_requirements_mock.assert_called_once_with()

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
            self.builder.build_src_dir, self.builder.checksums_path)

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_clean(self, utils_mock):
        self.builder.clean()
        utils_mock.assert_has_calls([
            mock.call.remove(self.builder.build_dir),
            mock.call.create_dir(self.builder.build_dir),
            mock.call.remove_by_mask(self.builder.result_package_mask)])


class TestBaseBuildV1(BaseBuild):

    __test__ = True
    builder_class = BuildPluginV1

    meta = {
        'releases': BaseBuild.releases,
        'version': '1.2.3',
        'name': 'plugin_name'
    }

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_make_package(self, utils_mock):
        self.builder.make_package()
        tar_path = '/tmp/fuel_plugin/plugin_name-1.2.3.fp'

        utils_mock.make_tar_gz.assert_called_once_with(
            self.builder.build_src_dir,
            tar_path,
            'plugin_name-1.2.3')

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpm, createrepo, dpkg-scanpackages", '
            'install required commands and try again',
            self.builder._check_requirements)


class TestBaseBuildV2(BaseBuild):

    __test__ = True
    builder_class = BuildPluginV2
    meta = {
        'releases': BaseBuild.releases,
        'version': '1.2.3',
        'name': 'plugin_name',
        'title': 'Plugin title',
        'description': 'Description',
        'licenses': ['Apache', 'BSD'],
        'authors': ['author1', 'author2'],
        'homepage': 'url'
    }

    def path_from_plugin(self, plugin_path, path):
        return join_path(plugin_path, path)

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def check_make_package(self, builder, plugin_path, utils_mock):
        plugin_path = plugin_path

        utils_mock.get_current_year.return_value = '2014'
        builder.make_package()
        rpm_src_path = self.path_from_plugin(plugin_path,
                                             '.build/rpm/SOURCES')
        utils_mock.create_dir.assert_called_once_with(rpm_src_path)

        fp_dst = self.path_from_plugin(
            plugin_path, '.build/rpm/SOURCES/plugin_name-1.2.fp')

        utils_mock.make_tar_gz.assert_called_once_with(
            self.path_from_plugin(plugin_path, '.build/src'),
            fp_dst,
            'plugin_name-1.2')

        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))
        utils_mock.render_to_file.assert_called_once_with(
            spec_src,
            join_path(plugin_path, '.build/rpm/plugin_rpm.spec'),
            {'vendor': 'author1, author2',
             'description': 'Description',
             'license': 'Apache and BSD',
             'summary': 'Plugin title',
             'version': '1.2.3',
             'homepage': 'url',
             'name': 'plugin_name-1.2',
             'year': '2014'})

        utils_mock.exec_cmd.assert_called_once_with(
            'rpmbuild -vv --nodeps --define "_topdir {0}" -bb '
            '{1}'.format(
                self.path_from_plugin(plugin_path, '.build/rpm'),
                self.path_from_plugin(plugin_path,
                                      '.build/rpm/plugin_rpm.spec')))

        utils_mock.copy_files_in_dir.assert_called_once_with(
            self.path_from_plugin(plugin_path,
                                  '.build/rpm/RPMS/noarch/*.rpm'),
            plugin_path
        )

    def test_make_package(self):
        self.check_make_package(self.builder, self.plugin_path)

    def test_make_package_with_non_ascii_chars_in_path(self):
        plugin_path = '/tmp/тест/' + self.plugins_name

        builder = self.create_builder(plugin_path)

        self.check_make_package(builder, plugin_path)

    @mock.patch('fuel_plugin_builder.actions.build.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpmbuild, rpm, createrepo, '
            'dpkg-scanpackages", install required commands and try again',
            self.builder._check_requirements)

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_build_ubuntu_repos(self, utils_mock):
        path = '/repo/path'
        self.builder.build_ubuntu_repos([path])
        utils_mock.exec_piped_cmds.assert_called_once_with(
            ['dpkg-scanpackages .', 'gzip -c9 > Packages.gz'],
            cwd=path)
        release_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.release_tmpl_src_path))
        utils_mock.render_to_file.assert_called_once_with(
            release_src,
            '/repo/path/Release',
            {'major_version': '1.2',
             'plugin_name': 'plugin_name'})


class TestBaseBuildV3(BaseBuild):

    __test__ = True
    builder_class = BuildPluginV3
    meta = {
        'releases': BaseBuild.releases,
        'version': '1.2.3',
        'name': 'plugin_name',
        'title': 'Plugin title',
        'description': 'Description',
        'licenses': ['Apache', 'BSD'],
        'authors': ['author1', 'author2'],
        'homepage': 'url'
    }

    def path_from_plugin(self, path):
        return join_path(self.plugin_path, path)

    @mock.patch('fuel_plugin_builder.actions.build.utils')
    def test_make_package(self, utils_mock):
        utils_mock.get_current_year.return_value = '2014'
        utils_mock.read_if_exist.side_effect = ['echo uninst', 'echo preinst',
                                                'echo postinst']
        self.builder.make_package()
        rpm_src_path = self.path_from_plugin('.build/rpm/SOURCES')
        utils_mock.create_dir.assert_called_once_with(rpm_src_path)

        fp_dst = self.path_from_plugin('.build/rpm/SOURCES/plugin_name-1.2.fp')
        utils_mock.make_tar_gz.assert_called_once_with(
            self.path_from_plugin('.build/src'),
            fp_dst,
            'plugin_name-1.2')

        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))
        utils_mock.render_to_file.assert_called_once_with(
            spec_src,
            join_path(self.plugin_path, '.build/rpm/plugin_rpm.spec'),
            {'vendor': 'author1, author2',
             'description': 'Description',
             'license': 'Apache and BSD',
             'summary': 'Plugin title',
             'version': '1.2.3',
             'homepage': 'url',
             'name': 'plugin_name-1.2',
             'year': '2014',
             'preinstall_hook': 'echo preinst',
             'postinstall_hook': 'echo postinst',
             'uninstall_hook': 'echo uninst'})

        utils_mock.exec_cmd.assert_called_once_with(
            'rpmbuild -vv --nodeps --define "_topdir {0}" -bb '
            '{1}'.format(
                self.path_from_plugin('.build/rpm'),
                self.path_from_plugin('.build/rpm/plugin_rpm.spec')))

        utils_mock.copy_files_in_dir.assert_called_once_with(
            self.path_from_plugin('.build/rpm/RPMS/noarch/*.rpm'),
            self.plugin_path)

        utils_mock.read_if_exist.assert_has_calls([
            mock.call(self.path_from_plugin('uninstall.sh')),
            mock.call(self.path_from_plugin('pre_install.sh')),
            mock.call(self.path_from_plugin('post_install.sh'))])
