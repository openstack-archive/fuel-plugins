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

import logging

from os.path import join as join_path

from fuel_plugin_builder.actions import BaseAction
from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder.validators import ValidatorManager

logger = logging.getLogger(__name__)


class BuildPlugin(BaseAction):

    requires = ['rpm', 'createrepo', 'dpkg-scanpackages']

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path
        self.pre_build_hook_path = join_path(plugin_path, 'pre_build_hook')
        self.meta = utils.parse_yaml(join_path(plugin_path, 'metadata.yaml'))
        self.build_dir = join_path(plugin_path, '.build')
        self.checksums_path = join_path(self.build_dir, 'checksums.sha1')

    def run(self):
        logger.debug('Start plugin building "%s"', self.plugin_path)
        self.run_pre_build_hook()
        self.check()
        self.build_repos()
        self.add_checksums_file()
        self.make_package()

    def run_pre_build_hook(self):
        if utils.which(self.pre_build_hook_path):
            utils.exec_cmd(self.pre_build_hook_path)

    def add_checksums_file(self):
        utils.create_checksums_file(self.build_dir, self.checksums_path)

    def make_package(self):
        full_name = '{0}-{1}'.format(self.meta['name'],
                                     self.meta['version'])
        tar_name = '{0}.fp'.format(full_name)
        tar_path = join_path(
            self.plugin_path,
            tar_name)

        if utils.exists(tar_path):
            utils.remove(tar_path)

        utils.make_tar_gz(self.build_dir, tar_path, full_name)

    def build_repos(self):
        utils.remove(self.build_dir)
        utils.create_dir(self.build_dir)

        utils.copy_files_in_dir(
            join_path(self.plugin_path, '*'),
            self.build_dir)

        releases_paths = {}
        for release in self.meta['releases']:
            releases_paths.setdefault(release['os'], [])
            releases_paths[release['os']].append(
                join_path(self.build_dir, release['repository_path']))

        self.build_ubuntu_repos(releases_paths.get('ubuntu', []))
        self.build_centos_repos(releases_paths.get('centos', []))

    @classmethod
    def build_ubuntu_repos(cls, releases_paths):
        for repo_path in releases_paths:
            utils.exec_cmd(
                'dpkg-scanpackages . | gzip -c9 > Packages.gz',
                cwd=repo_path)

    @classmethod
    def build_centos_repos(cls, releases_paths):
        for repo_path in releases_paths:
            repo_packages = join_path(repo_path, 'Packages')
            utils.create_dir(repo_packages)
            utils.move_files_in_dir(
                join_path(repo_path, '*.rpm'),
                repo_packages)
            utils.exec_cmd('createrepo -o {0} {0}'.format(repo_path))

    def check(self):
        self._check_requirements()
        self._check_structure()

    def _check_requirements(self):
        not_found = filter(lambda r: not utils.which(r), self.requires)

        if not_found:
            raise errors.FuelCannotFindCommandError(
                'Cannot find commands "{0}", '
                'install required commands and try again'.format(
                    ', '.join(not_found)))

    def _check_structure(self):
        ValidatorManager(self.plugin_path).get_validator().validate()
