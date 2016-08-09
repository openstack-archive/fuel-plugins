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

from .builder_base import BuilderBase
from fuel_plugin_builder import loaders
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class BuilderV1(BuilderBase):
    loader_class = loaders.PluginLoaderV1
    requires = ['rpm', 'createrepo', 'dpkg-scanpackages']

    @property
    def result_package_mask(self):
        return join_path(self.plugin_path, '{0}-*.fp'.format(self.name))

    def make_package(self):
        full_name = '{0}-{1}'.format(self.meta['name'],
                                     self.meta['version'])
        tar_name = '{0}.fp'.format(full_name)
        tar_path = join_path(
            self.plugin_path,
            tar_name)

        utils.make_tar_gz(self.build_src_dir, tar_path, full_name)
