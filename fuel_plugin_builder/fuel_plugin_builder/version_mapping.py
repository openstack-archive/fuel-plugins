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

from fuel_plugin_builder import errors
from fuel_plugin_builder.validators import ValidatorV1

latest_vesion = '1.0.0'

mapping = [
    {'version': '1.0.0',
     'validator': ValidatorV1,
     'templates': 'templates/v1/'}]


def get_plugin_for_version(version):
    """Retrieves data which are required for specific version of plugin

    :param str version: version of package
    :returns: dict which contains
              'version' - package version
              'validator' - validator object
              'templates' - path to templates
    """
    data = filter(lambda p: p['version'] == version, mapping)

    if not data:
        raise errors.WrongPackageVersionError(
            'Wrong package version "{0}"'.format(version))

    return data[0]
