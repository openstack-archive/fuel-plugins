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

from fuel_plugin_builder import version_mapping


class ValidatorManager(object):

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def get_validator(self):
        validator = version_mapping.get_version_mapping_from_plugin(
            self.plugin_path)['validator']
        return validator(self.plugin_path)
