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

import os
import logging
import yaml
import glob
import tarfile

from fuel_plugin_builder import utils
from fuel_plugin_builder import errors
from fuel_plugin_builder.actions import BaseAction


logger = logging.getLogger(__name__)


class BuildPlugin(BaseAction):

    requires = ['rpm', 'createrepo', 'dpkg-scanpackages']

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path
        self.pre_build_hook_path = os.path.join(plugin_path, 'pre_build_hook')

        self.centos_repo_path = os.path.join(plugin_path, 'repos/centos')
        self.ubuntu_repo_path = os.path.join(plugin_path, 'repos/ubuntu')
        self.meta = yaml.load(open(os.path.join(plugin_path, 'metadata.yaml')))
        self.build_dir = os.path.join(plugin_path, '.build')

    def run(self):
        self.build_repos()
        self.make_tarball()

    def make_tarball(self):
        full_name = '{0}-{1}'.format(self.meta['name'],
                                    self.meta['version'])
        tar_name = '{0}.tar'.format(full_name)
        tar_path = os.path.join(
            self.plugin_path,
            tar_name)

        if utils.exists(tar_path):
            utils.exec_cmd('rm -f {0}'.format(tar_path))

        tar = tarfile.open(tar_path, 'w')
        tar.add(self.build_dir, arcname=full_name)
        tar.close()

    def build_repos(self):
        # TODO(eli): it really needs to be refactored
        # it was written right before the demo on the fly
        if utils.which(self.pre_build_hook_path):
            utils.exec_cmd(self.pre_build_hook_path)

        utils.create_dir(self.build_dir)
        utils.exec_cmd('rm -rf {0}'.format(os.path.join(self.build_dir, '*')))
        utils.exec_cmd(
            'cp -r {0} {1}'.format(
                os.path.join(self.plugin_path, '*'),
                self.build_dir))

        releases_paths = {}
        for release in self.meta['releases']:
            releases_paths.setdefault(release['os'], [])
            releases_paths[release['os']].append(
                os.path.join(self.build_dir, release['repository_path']))

        for repo_path in releases_paths.get('centos', []):
            repo_packages = os.path.join(repo_path, 'Packages')
            utils.create_dir(repo_packages)
            rpms = os.path.join(repo_path, '*.rpm')
            if glob.glob(rpms):
                utils.exec_cmd('cp {0} {1}'.format(
                    os.path.join(repo_path, '*.rpm'),
                    repo_packages))
            utils.exec_cmd('createrepo -o {0} {1}'.format(repo_path,
                                                          repo_packages))

        for repo_path in releases_paths.get('ubuntu', []):
            utils.exec_cmd(
                'dpkg-scanpackages {0} | gzip -c9 > {1}'.format(
                    repo_path,
                    os.path.join(repo_path, 'Packages.gz')))

    def check(self):
        not_found = filter(lambda r: not utils.which(r), self.requires)

        if not_found:
            raise errors.FuelCannotFindCommandError(
                'Cannot find commands "{0}", '
                'install required commands and try again'.format(
                    ','.join(not_found)))
