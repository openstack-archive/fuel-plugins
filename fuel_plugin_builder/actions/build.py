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

from __future__ import unicode_literals

import logging

import fuel_plugin_builder

logger = logging.getLogger(__name__)


def make_builder(plugin_path):
    """Creates build object.

    :param str plugin_path: path to the plugin
    :returns: specific version of builder object
    """
    builder = \
        fuel_plugin_builder.version_mapping.get_plugin_package_config_for_path(
            plugin_path
        )['builder']
    return builder(plugin_path)
