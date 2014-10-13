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

    def run(self):
        if utils.which(self.pre_build_hook_path):
            utils.exec_cmd(self.pre_build_hook_path)

        utils.exec_cmd(
            'createrepo -o {0} {1}'.format(
                os.path.join(self.centos_repo_path, 'x86_64'),
                os.path.join(self.centos_repo_path, 'x86_64', 'Packages')))
        utils.exec_cmd(
            'dpkg-scanpackages {0} | gzip -c9 > {1}'.format(
                self.ubuntu_repo_path,
                os.path.join(self.ubuntu_repo_path, 'Packages.gz')))

    def check(self):
        not_found = filter(lambda r: not utils.which(r), self.requires)

        if not_found:
            raise errors.FuelCannotFindCommandError(
                'Cannot find commands "{0}", '
                'install required commands and try again'.format(
                    ','.join(not_found)))
