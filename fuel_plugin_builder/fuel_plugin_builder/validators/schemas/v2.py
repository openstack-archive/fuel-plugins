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

from base import PLUGIN_RELEASE_SCHEMA
from base import METADATA_SCHEMA
from base import POSITIVE_INTEGER
from base import PUPPET_PARAMETERS
from base import SHELL_PARAMETERS
from base import TASK_BASE_PARAMETERS
from base import PLUGIN_RELEASE_SCHEMA
from base import TASK_SCHEMA
from base import TASKS_SCHEMA
from base import ATTR_ELEMENT_SCHEMA
from base import ATTR_META_SCHEMA
from base import ATTR_ROOT_SCHEMA

TASK_SCHEMA['properties']['type'] = {'enum': ['puppet', 'shell', 'reboot']}

REBOOT_PARAMETERS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['timeout'],
    'properties': {
        'timeout': POSITIVE_INTEGER}}
