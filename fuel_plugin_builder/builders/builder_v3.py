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

from builders import BuilderV2
from fuel_plugin_builder import loaders
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class BuilderV3(BuilderV2):
    rpm_spec_src_path = 'templates/v3/build/plugin_rpm.spec.mako'
    release_tmpl_src_path = 'templates/v3/build/Release.mako'

    loader_class = loaders.LoaderV3

    def _make_data_for_template(self):
        data = super(BuilderV3, self)._make_data_for_template()

        uninst = utils.read_if_exist(
            join_path(self.plugin_path, "uninstall.sh"))

        preinst = utils.read_if_exist(
            join_path(self.plugin_path, "pre_install.sh"))

        postinst = utils.read_if_exist(
            join_path(self.plugin_path, "post_install.sh"))

        data.update({
            'postinstall_hook': postinst,
            'preinstall_hook': preinst,
            'uninstall_hook': uninst
        })

        return data
