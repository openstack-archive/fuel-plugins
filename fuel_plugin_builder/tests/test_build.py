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

import os
from os.path import join as join_path

import mock

import reports
from builders import BaseBuildPlugin
from builders import BuildPluginV1
from builders import BuildPluginV2
from builders import BuildPluginV3
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase


class BaseBuildTestCase(BaseTestCase):
    # Prevent test runner to run tests in base
    __test__ = False
    # Redefine class
    BuilderClass = None

    fake_metadata = None

    releases = [
        {'os': 'ubuntu',
         'deployment_scripts_path': 'deployment_scripts_path',
         'repository_path': 'repository_path'}]

    def setUp(self):
        self.plugin_path = '/tmp/fuel_plugin'
        self.builder = self._create_builder(self.plugin_path)

    def _create_builder(self, plugin_path):
        with mock.patch(
                'fuel_plugin_builder.loaders.base.BaseLoader.load',
                return_value=(self.fake_metadata, reports.ReportNode())):
            return self.BuilderClass(plugin_path)

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
                self.BuilderClass, 'build_ubuntu_repos') as build_ubuntu_mock:
            with mock.patch.object(
                    self.BuilderClass,
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
            ['dpkg-scanpackages .', 'gzip -c9 > Packages.gz'],
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

    @mock.patch.object(BaseBuildPlugin, '_check_requirements')
    @mock.patch.object(BaseBuildPlugin, '_validate')
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


class TestBaseBuildV1(BaseBuildTestCase):
    __test__ = True
    BuilderClass = BuildPluginV1

    fake_metadata = {
        'releases': BaseBuildTestCase.releases,
        'version': '1.2.3',
        'name': 'plugin_name'
    }

    @mock.patch('fuel_plugin_builder.utils.make_tar_gz')
    def test_make_package(self, make_tar_gz_m):
        self.builder.make_package()
        tar_path = '/tmp/fuel_plugin/plugin_name-1.2.3.fp'

        make_tar_gz_m.assert_called_once_with(
            self.builder.build_src_dir,
            tar_path,
            'plugin_name-1.2.3')

    @mock.patch('fuel_plugin_builder.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpm, createrepo, dpkg-scanpackages", '
            'install required commands and try again',
            self.builder._check_requirements)


class TestBaseBuildV2(BaseBuildTestCase):
    __test__ = True
    plugin_path = os.path.abspath('./templates/v2/plugin_data')
    BuilderClass = BuildPluginV2
    fake_metadata = {
        'releases': BaseBuildTestCase.releases,
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

    # fixme(ikutukov): investigate better approach to utils mocking
    @mock.patch('fuel_plugin_builder.utils.get_current_year')
    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.make_tar_gz')
    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    @mock.patch('fuel_plugin_builder.utils.exec_cmd')
    @mock.patch('fuel_plugin_builder.utils.copy_files_in_dir')
    def check_make_package(self, builder, plugin_path,
                           copy_files_in_dir_m, exec_cmd_m,
                           load_template_and_render_to_file_m, make_tar_gz_m,
                           create_dir_m, get_current_year_m):
        get_current_year_m.return_value = '2016'
        builder.make_package()
        rpm_src_path = self.path_from_plugin(plugin_path,
                                             '.build/rpm/SOURCES')
        create_dir_m.assert_called_once_with(rpm_src_path)

        fp_dst = self.path_from_plugin(
            plugin_path, '.build/rpm/SOURCES/plugin_name-1.2.fp')

        make_tar_gz_m.assert_called_once_with(
            self.path_from_plugin(plugin_path, '.build/src'),
            fp_dst,
            'plugin_name-1.2')

        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))
        load_template_and_render_to_file_m.assert_called_once_with(
            spec_src,
            join_path(plugin_path, '.build/rpm/plugin_rpm.spec'),
            {
                'vendor': 'author1, author2',
                'description': 'Description',
                'license': 'Apache and BSD',
                'summary': 'Plugin title',
                'version': '1.2.3',
                'homepage': 'url',
                'name': 'plugin_name-1.2',
                'year': '2016'
            }
        )

        exec_cmd_m.assert_called_once_with(
            'rpmbuild -vv --nodeps --define "_topdir {0}" -bb '
            '{1}'.format(
                self.path_from_plugin(plugin_path, '.build/rpm'),
                self.path_from_plugin(plugin_path,
                                      '.build/rpm/plugin_rpm.spec')))

        copy_files_in_dir_m.assert_called_once_with(
            self.path_from_plugin(plugin_path,
                                  '.build/rpm/RPMS/noarch/*.rpm'),
            plugin_path
        )

    def test_make_package(self):
        self.check_make_package(self.builder, self.plugin_path)

    def test_make_package_with_non_ascii_chars_in_path(self):
        plugin_path = '/tmp/тест/fuel_plugin'

        builder = self._create_builder(plugin_path)

        self.check_make_package(builder, plugin_path)

    @mock.patch('fuel_plugin_builder.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpmbuild, rpm, createrepo, '
            'dpkg-scanpackages", install required commands and try again',
            self.builder._check_requirements)

    @mock.patch('fuel_plugin_builder.utils.exec_piped_cmds')
    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    def test_build_ubuntu_repos(
            self, load_template_and_render_to_file_m, exec_piped_cmds_m):
        path = '/repo/path'
        self.builder.build_ubuntu_repos([path])
        exec_piped_cmds_m.assert_called_once_with(
            [
                'dpkg-scanpackages .',
                'gzip -c9 > Packages.gz'
            ],
            cwd=path
        )
        # self.
        release_src = os.path.abspath(
            join_path(
                os.path.dirname(__file__),
                '..',
                self.builder.release_tmpl_src_path
            )
        )

        # print "RS", release_src
        load_template_and_render_to_file_m.assert_called_once_with(
            release_src,
            '/repo/path/Release',
            {
                'major_version': '1.2',
                'plugin_name': 'plugin_name'
            }
        )


class TestBaseBuildV3(BaseBuildTestCase):
    __test__ = True
    BuilderClass = BuildPluginV3
    plugin_path = os.path.abspath('./templates/v3/plugin_data')

    fake_metadata = {
        'releases': BaseBuildTestCase.releases,
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

    # fixme(ikutukov): investigate better approach to utils mocking
    @mock.patch('fuel_plugin_builder.utils.get_current_year')
    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.make_tar_gz')
    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    @mock.patch('fuel_plugin_builder.utils.exec_cmd')
    @mock.patch('fuel_plugin_builder.utils.copy_files_in_dir')
    @mock.patch('fuel_plugin_builder.utils.read_if_exist')
    def check_make_package(self, builder, plugin_path, read_if_exist_m,
                           copy_files_in_dir_m, exec_cmd_m,
                           load_template_and_render_to_file_m, make_tar_gz_m,
                           create_dir_m, get_current_year_m):
        get_current_year_m.return_value = '2014'
        read_if_exist_m.side_effect = ['echo uninst', 'echo preinst',
                                                'echo postinst']
        self.builder.make_package()
        rpm_src_path = self.path_from_plugin('.build/rpm/SOURCES')
        create_dir_m.assert_called_once_with(rpm_src_path)

        fp_dst = self.path_from_plugin('.build/rpm/SOURCES/plugin_name-1.2.fp')
        make_tar_gz_m.assert_called_once_with(
            self.path_from_plugin('.build/src'),
            fp_dst,
            'plugin_name-1.2')

        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))
        load_template_and_render_to_file_m.assert_called_once_with(
            spec_src,
            join_path(self.plugin_path, '.build/rpm/plugin_rpm.spec'),
            {
                'vendor': 'author1, author2',
                'description': 'Description',
                'license': 'Apache and BSD',
                'summary': 'Plugin title',
                'version': '1.2.3',
                'homepage': 'url',
                'name': 'plugin_name-1.2',
                'year': '2014',
                'preinstall_hook': 'echo preinst',
                'postinstall_hook': 'echo postinst',
                'uninstall_hook': 'echo uninst'
            }
        )

        exec_cmd_m.assert_called_once_with(
            'rpmbuild -vv --nodeps --define "_topdir {0}" -bb '
            '{1}'.format(
                self.path_from_plugin('.build/rpm'),
                self.path_from_plugin('.build/rpm/plugin_rpm.spec')))

        copy_files_in_dir_m.assert_called_once_with(
            self.path_from_plugin('.build/rpm/RPMS/noarch/*.rpm'),
            self.plugin_path)

        read_if_exist_m.assert_has_calls([
            mock.call(self.path_from_plugin('uninstall.sh')),
            mock.call(self.path_from_plugin('pre_install.sh')),
            mock.call(self.path_from_plugin('post_install.sh'))])
