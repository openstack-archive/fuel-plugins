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

import abc
import logging
from os.path import join as join_path

import fuel_plugin_builder
from fuel_plugin_builder import errors
from fuel_plugin_builder import actions
from fuel_plugin_builder import loaders
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class BuilderBase(actions.BaseAction):
    loader_class = loaders.PluginLoaderV1

    @abc.abstractproperty
    def requires(self):
        """Should return a list of commands which
        are required for the builder
        """

    @abc.abstractproperty
    def result_package_mask(self):
        """Should return mask for built package
        """

    @abc.abstractmethod
    def make_package(self):
        """Method should be implemented in child classes
        """

    def __init__(self, plugin_path, loader=None):
        self.plugin_path = plugin_path
        if loader:
            self.loader = loader
        else:
            self.loader = self.loader_class(plugin_path)

        self.pre_build_hook_cmd = './pre_build_hook'
        self.meta = self.loader.load(
            self.plugin_path
        )
        if self.meta.report.is_failed():
            raise Exception(self.meta.report.render())
        self.build_dir = join_path(self.plugin_path, '.build')
        self.build_src_dir = join_path(self.build_dir, 'src')
        self.checksums_path = join_path(self.build_src_dir, 'checksums.sha1')
        self.name = self.meta['name']

    def run(self):
        logger.debug('Start plugin building "%s"', self.plugin_path)
        self.clean()
        self.run_pre_build_hook()
        self.check()
        self.build_repos()
        self.add_checksums_file()
        self.make_package()

    def clean(self):
        utils.remove(self.build_dir)
        utils.create_dir(self.build_dir)
        utils.remove_by_mask(self.result_package_mask)

    def run_pre_build_hook(self):
        if utils.which(join_path(self.plugin_path, self.pre_build_hook_cmd)):
            utils.exec_cmd(self.pre_build_hook_cmd, self.plugin_path)

    def add_checksums_file(self):
        utils.create_checksums_file(self.build_src_dir, self.checksums_path)

    def build_repos(self):
        utils.create_dir(self.build_src_dir)

        utils.copy_files_in_dir(
            join_path(self.plugin_path, '*'),
            self.build_src_dir)

        releases_paths = {}
        for release in self.meta['releases']:
            releases_paths.setdefault(release['os'], [])
            releases_paths[release['os']].append(
                join_path(self.build_src_dir, release['repository_path']))

        self.build_ubuntu_repos(releases_paths.get('ubuntu', []))
        self.build_centos_repos(releases_paths.get('centos', []))

    def build_ubuntu_repos(cls, releases_paths):
        for repo_path in releases_paths:
            utils.exec_piped_cmds(
                ['dpkg-scanpackages -m .', 'gzip -c9 > Packages.gz'],
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
        self._validate()

    def _check_requirements(self):
        not_found = filter(lambda r: not utils.which(r), self.requires)

        if not_found:
            raise errors.FuelCannotFindCommandError(
                'Cannot find commands "{0}", '
                'install required commands and try again'.format(
                    ', '.join(not_found)))

    def _validate(self):
        fuel_plugin_builder.version_mapping.get_validator(self.plugin_path).validate()
