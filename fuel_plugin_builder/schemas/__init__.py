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

#
# Please, be kindly reminded about data schema versioning policy and its
# nuances:
#
# Fuel Plugin Builder(FPB) is on intersection of several lines of versioning
# subsystems and APIs making the data schema tricky (as small as it possible)
#
# ``Tasks`` version that are defined by changes in data flow chain
# between of API Fuel, Astute, Fuel Library and QA environment. In theory, all
# versions of this tasks could be delivered now, on practice v1.0.0 is not
# even close to way you may want to configure what Nailgun do.
#
# ``Plugin package`` version as well FPB version is semver where major going
# up on all changes in plugin format and any changes of data schema inside it
# that could affect internal and third-party plugins developers.
#
# ``FPB own version`` FPB not releasing together with Fuel, but respecting
# Fuel milestones. Fuel still holds a great backward compatibility with plugins
# 3 and even more major releases ago, so there is no rush to roll up changes
# that will open new sometimes experimental functionality. Everyone who want
# to work with new features is free to clone and use latest master of FPB to
# build new format of plugin packages.
#
#
# So we have hypothetical versions snapshot:
#
# FPB version 4.1.0
# Plugins package version 4.0.0
# Fuel version 9.0.1
# Tasks version 2.1.0
#

from attributes import attributes_v4_0_0
from common import common_v6_0
from components import components_v4_0_0
from graph import graph_v5_0_0
from network_roles import network_roles_v7_0
from release import release_v9_1
from roles import roles_v3_0_0
from volumes import volumes_v7_0

from metadata import metadata_v9_1

from task import task_v2_1_0
