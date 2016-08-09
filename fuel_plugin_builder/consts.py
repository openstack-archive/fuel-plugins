# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
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

# Default files encoding
DEFAULT_ENCODING = 'utf-8'

# In order of preference
SUPPORTED_FORMATS = ('yaml', 'json',)

# Used during plugin build
TAR_PARAMETERS = 'w:gz'

# Template extension
TEMPLATE_EXTENSION = 'mako'

# Latest plugin package version
LATEST_VERSION = '5.0.0'

# Plugin name pattern that are used in schemas and builder
PLUGIN_NAME_PATTERN = '^[a-z0-9_-]+$'

# suffix for the metadata.yaml paths filds
PATHS_SUFFIX = '_path'
