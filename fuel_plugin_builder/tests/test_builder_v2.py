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

import os
from os.path import join as join_path

import mock

from fuel_plugin_builder import builders
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.test_builder_base import BaseBuildTestCase


class TestBuilderV2(BaseBuildTestCase):
    __test__ = True
    builder_class = builders.BuilderV2
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
            ['dpkg-scanpackages -m .', 'gzip -c9 > Packages.gz'],
            cwd=path)
        release_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.release_tmpl_src_path))
        load_template_and_render_to_file_m.assert_called_once_with(
            release_src,
            '/repo/path/Release',
            {
                'major_version': '1.2',
                'plugin_name': 'plugin_name'
            }
        )
