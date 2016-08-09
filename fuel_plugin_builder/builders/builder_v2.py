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

import logging
import os
from os.path import join as join_path

from builders import BuilderBase
from fuel_plugin_builder import loaders
import utils

logger = logging.getLogger(__name__)


class BuilderV2(BuilderBase):
    loader_class = loaders.LoaderV1  # LoaderV1 is not type

    requires = ['rpmbuild', 'rpm', 'createrepo', 'dpkg-scanpackages']

    rpm_spec_src_path = 'templates/v2/build/plugin_rpm.spec.mako'
    release_tmpl_src_path = 'templates/v2/build/Release.mako'

    def __init__(self, *args, **kwargs):
        super(BuilderV2, self).__init__(*args, **kwargs)

        self.plugin_version, self.full_version = utils.version_split_name_rpm(
            self.meta['version'])

        self.rpm_path = os.path.abspath(
            join_path(self.plugin_path, '.build', 'rpm'))

        self.rpm_src_path = join_path(self.rpm_path, 'SOURCES')
        self.full_name = '{0}-{1}'.format(
            self.meta['name'], self.plugin_version)

        tar_name = '{0}.fp'.format(self.full_name)
        self.tar_path = join_path(self.rpm_src_path, tar_name)

        fpb_dir = join_path(os.path.dirname(__file__), '..')

        self.spec_src = os.path.abspath(join_path(
            fpb_dir, self.rpm_spec_src_path))

        self.release_tmpl_src = os.path.abspath(join_path(
            fpb_dir, self.release_tmpl_src_path))

        self.spec_dst = join_path(self.rpm_path, 'plugin_rpm.spec')

        self.rpm_packages_mask = join_path(
            self.rpm_path, 'RPMS', 'noarch', '*.rpm')

    @property
    def result_package_mask(self):
        return join_path(
            self.plugin_path, '{0}-*.noarch.rpm'.format(self.name))

    def make_package(self):
        """Builds rpm package
        """
        utils.create_dir(self.rpm_src_path)

        utils.make_tar_gz(self.build_src_dir, self.tar_path, self.full_name)
        utils.load_template_and_render_to_file(
            self.spec_src,
            self.spec_dst,
            self._make_data_for_template())

        utils.exec_cmd(
            'rpmbuild -vv --nodeps --define "_topdir {0}" '
            '-bb {1}'.format(self.rpm_path, self.spec_dst))
        utils.copy_files_in_dir(self.rpm_packages_mask, self.plugin_path)

    def _make_data_for_template(self):
        """Generates data for spec template

        :returns: dictionary with required data
        """
        return {
            'name': self.full_name,
            'version': self.full_version,
            'summary': self.meta['title'],
            'description': self.meta['description'],
            'license': ' and '.join(self.meta.get('licenses', [])),
            'homepage': self.meta.get('homepage'),
            'vendor': ', '.join(self.meta.get('authors', [])),
            'year': utils.get_current_year()}

    def build_ubuntu_repos(self, releases_paths):
        for repo_path in releases_paths:
            utils.exec_piped_cmds(
                ['dpkg-scanpackages .', 'gzip -c9 > Packages.gz'],
                cwd=repo_path)
            release_path = join_path(repo_path, 'Release')
            utils.load_template_and_render_to_file(
                self.release_tmpl_src,
                release_path,
                {
                    'plugin_name': self.meta['name'],
                    'major_version': self.plugin_version
                }
            )
