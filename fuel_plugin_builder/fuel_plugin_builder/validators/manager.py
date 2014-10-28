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

from os.path import join as join_path

from fuel_plugin_builder import utils


class ValidatorManager(object):

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path
        self.meta = utils.parse_yaml(join_path(plugin_path, 'metadata.yaml'))
        self.package_version = self.meta.get('package_version')

    def get_validator(self):
        # NOTE(eli): it's here because of circular dependency problem
        from fuel_plugin_builder.version_mapping import get_plugin_for_version

        validator = get_plugin_for_version(self.package_version)['validator']
        return validator(self.plugin_path)
