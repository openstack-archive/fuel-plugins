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
import os
import six

from fuel_plugin_builder.actions import BaseAction
from fuel_plugin_builder import utils
from fuel_plugin_builder import errors

logger = logging.getLogger(__name__)


class CreatePlugin(BaseAction):

    plugin_structure = [
        {'path': 'metadata.yaml',
         'action': 'render',
         'from':'metadata.yaml'},

        {'path': 'environment_config.yaml',
         'action': 'render',
         'from':'environment_config.yaml'},

        {'path': 'LICENSE',
         'action': 'copy',
         'from':'LICENSE'},

        {'path': 'deployment_scripts',
         'action': 'mkdir'},

        {'path': 'deployment_scripts/deploy.sh',
         'action': 'render',
         'from': 'deploy.sh'},

        {'path': 'README.md',
         'action': 'render',
         'from':'README.md'},

        {'path': 'repositories',
         'action': 'mkdir'},

        {'path': 'repositories/centos',
         'action': 'mkdir'},

        {'path': 'repositories/ubuntu',
         'action': 'mkdir'},

        {'path': 'tasks.yaml',
         'action': 'copy',
         'from': 'tasks.yaml'},

        {'path': '.gitignore',
         'action': 'copy',
         'from': '.gitignore'},

        {'path': 'pre_build_hook',
         'action': 'copy',
         'from': 'pre_build_hook'},

        {'path': 'install',
         'action': 'render',
         'from': 'install'},

        {'path': 'register_plugin.py',
         'action': 'copy',
         'from': 'register_plugin.py'}]

    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')

    def __init__(self, plugin_path):
        self.plugin_name = utils.basename(plugin_path)
        self.plugin_path = plugin_path
        self.render_ctx = {
            'plugin_name': self.plugin_name,
            'plugin_version': '0.1.0'}

    def check(self):
        if utils.exists(self.plugin_path):
            raise errors.PluginDirectoryExistsError(
                'Plugins directory {0} already exists, '
                'choose anothe name'.format(self.plugin_path))

    def run(self):
        utils.create_dir(self.plugin_path)

        for conf in self.plugin_structure:
            if conf['action'] == 'render':
                utils.render_to_file(
                    os.path.join(self.template_dir, conf['from']),
                    os.path.join(self.plugin_path, conf['path']),
                    self.render_ctx)
                utils.copy_file_permissions(
                    os.path.join(self.template_dir, conf['from']),
                    os.path.join(self.plugin_path, conf['path']))
            elif conf['action'] == 'mkdir':
                utils.create_dir(os.path.join(
                    self.plugin_path,
                    conf['path']))
            elif conf['action'] == 'copy':
                utils.copy_file(
                    os.path.join(self.template_dir, conf['from']),
                    os.path.join(self.plugin_path, conf['path']))
