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
from fuel_plugin_builder.tests.test_builder_base import BaseBuildTestCase


class TestBuilderV3(BaseBuildTestCase):
    __test__ = True
    builder_class = builders.PluginBuilderV3

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

    @mock.patch('fuel_plugin_builder.utils.get_current_year')
    @mock.patch('fuel_plugin_builder.utils.create_dir')
    @mock.patch('fuel_plugin_builder.utils.make_tar_gz')
    @mock.patch('fuel_plugin_builder.utils.exec_cmd')
    @mock.patch('fuel_plugin_builder.utils.copy_files_in_dir')
    @mock.patch('fuel_plugin_builder.utils.FilesManager.load')
    def _test_make_package(self, load_m,
                           copy_files_in_dir_m, exec_cmd_m,
                           make_tar_gz_m,
                           create_dir_m, get_current_year_m):
        get_current_year_m.return_value = '2014'
        load_m.side_effect = ['echo uninst', 'echo preinst', 'echo postinst']
        self.builder.make_package()
        rpm_src_path = self.path_from_plugin('.build/rpm/SOURCES')
        create_dir_m.assert_called_once_with(rpm_src_path)

        fp_dst = self.path_from_plugin('.build/rpm/SOURCES/plugin_name-1.2.fp')
        make_tar_gz_m.assert_called_once_with(
            self.path_from_plugin('.build/src'),
            fp_dst,
            'plugin_name-1.2')

        exec_cmd_m.assert_called_once_with(
            'rpmbuild -vv --nodeps --define "_topdir {0}" -bb '
            '{1}'.format(
                self.path_from_plugin('.build/rpm'),
                self.path_from_plugin('.build/rpm/plugin_rpm.spec')))

        copy_files_in_dir_m.assert_called_once_with(
            self.path_from_plugin('.build/rpm/RPMS/noarch/*.rpm'),
            self.plugin_path)

        load_m.assert_has_calls([
            mock.call(self.path_from_plugin('uninstall.sh')),
            mock.call(self.path_from_plugin('pre_install.sh')),
            mock.call(self.path_from_plugin('post_install.sh'))])

    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    def test_make_package(self, load_template_and_render_to_file_m):
        self._test_make_package()
        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))

        load_template_and_render_to_file_m.assert_called_once_with(
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
             'uninstall_hook': 'echo uninst',
             'build_version': '1'})

    @mock.patch('fuel_plugin_builder.utils.load_template_and_render_to_file')
    def test_make_package_with_build_version(
            self, load_template_and_render_to_file_m):
        meta = {
            'releases': BaseBuildTestCase.releases,
            'version': '1.2.3',
            'name': 'plugin_name',
            'title': 'Plugin title',
            'description': 'Description',
            'licenses': ['Apache', 'BSD'],
            'authors': ['author1', 'author2'],
            'homepage': 'url',
            'build_version': '34'
        }
        self.builder = self._create_builder(
            self.plugin_path, fake_metadata=meta)
        self._test_make_package()

        spec_src = os.path.abspath(join_path(
            os.path.dirname(__file__), '..',
            self.builder.rpm_spec_src_path))

        load_template_and_render_to_file_m.assert_called_once_with(
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
             'uninstall_hook': 'echo uninst',
             'build_version': '34'})
