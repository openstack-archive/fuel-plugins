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

from fuel_plugin_builder.actions import BaseAction
from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder import version_mapping

logger = logging.getLogger(__name__)


class CreatePlugin(BaseAction):

    def __init__(self, plugin_path):
        self.plugin_name = utils.basename(plugin_path.rstrip('/'))
        self.plugin_path = plugin_path
        self.render_ctx = {
            'plugin_name': self.plugin_name,
            'plugin_version': '1.0.0'}
        self.template_path = version_mapping.get_plugin_for_version(
            version_mapping.latest_vesion)['templates']

    def check(self):
        if utils.exists(self.plugin_path):
            raise errors.PluginDirectoryExistsError(
                'Plugins directory {0} already exists, '
                'choose another name'.format(self.plugin_path))

    def run(self):
        logger.debug('Start plugin creation "%s"', self.plugin_path)
        self.check()

        template_dir = os.path.join(
            os.path.dirname(__file__), '..', self.template_path)

        utils.copy(template_dir, self.plugin_path)
        utils.render_files_in_dir(self.plugin_path, self.render_ctx)
