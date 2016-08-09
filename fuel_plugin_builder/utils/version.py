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

import distutils


def strict_version(minimal_fuel_version):
    return distutils.version.StrictVersion(minimal_fuel_version)


def version_split_name_rpm(version):
    version_tuple = distutils.StrictVersion(version).version
    major = '.'.join(map(str, version_tuple[0:2]))
    minor = version

    return major, minor
