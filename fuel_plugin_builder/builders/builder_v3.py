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
from os.path import join as join_path

from fuel_plugin_builder.builders.builder_v2 import PluginBuilderV2
from fuel_plugin_builder import errors
from fuel_plugin_builder import loaders
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class PluginBuilderV3(PluginBuilderV2):
    rpm_spec_src_path = 'templates/v3/build/plugin_rpm.spec.mako'
    release_tmpl_src_path = 'templates/v3/build/Release.mako'

    loader_class = loaders.PluginLoaderV3

    def _make_data_for_template(self):
        data = super(PluginBuilderV3, self)._make_data_for_template()

        data['build_version'] = str(self.data.get('build_version', '1'))
        fm = utils.FilesManager()
        for key, script_file in (
            ('uninstall_hook', 'uninstall.sh'),
            ('preinstall_hook', 'pre_install.sh'),
            ('postinstall_hook', 'post_install.sh')
        ):
            try:
                data[key] = fm.load(
                    join_path(self.plugin_path, script_file))
            except errors.NoPluginFileFound:
                data[key] = ''
        return data
