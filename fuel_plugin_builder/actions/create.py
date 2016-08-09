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
import re

import fuel_plugin_builder
from fuel_plugin_builder import consts
from fuel_plugin_builder import errors
from .base import BaseAction
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class CreatePlugin(BaseAction):
    plugin_name_pattern = re.compile(consts.PLUGIN_NAME_PATTERN)

    def __init__(self, plugin_path, package_version=None):
        self.plugin_name = utils.basename(plugin_path.rstrip('/'))
        self.plugin_path = plugin_path
        self.package_version = (package_version or
                                consts.LATEST_VERSION)

        self.render_ctx = {'plugin_name': self.plugin_name}
        self.template_paths = fuel_plugin_builder.version_mapping.get_config_for_plugin_package_version(
            self.package_version)['templates']

    def check(self):
        if utils.is_exists(self.plugin_path):
            raise errors.PluginDirectoryExistsError(
                'Plugins directory {0} already exists, '
                'choose another name'.format(self.plugin_path))

        if not self.plugin_name_pattern.match(self.plugin_name):
            raise errors.ValidationError(
                "Plugin name is invalid, use only lower "
                "case letters, numbers, '_', '-' symbols")

    def run(self):
        logger.debug('Start plugin creation "%s"', self.plugin_path)
        self.check()

        for template_path in self.template_paths:
            template_dir = os.path.join(
                os.path.dirname(__file__), '..', template_path)

            utils.copy(template_dir, self.plugin_path)
            utils.render_files_in_dir(self.plugin_path, self.render_ctx)
