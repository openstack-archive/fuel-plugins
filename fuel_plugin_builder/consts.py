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


# Only lower case letters, numbers, '_', '-' symbols
PLUGIN_NAME_PATTERN = '^[a-z0-9_-]+$'

# where the plugin root file located relative to the plugin root
ROOT_FILE_PATH_AND_NAME = './metadata'  # tail suppose extension

# in order of preference
SUPPORTED_FORMATS = ('yaml', 'json',)

# used during plugin build
TAR_PARAMETERS = 'w:gz'


# size of the new level text indent when rendering report
REPORT_INDENT_SIZE = 4

# symbol to mark error nodes when rendering report
REPORT_FAILURE_POINTER = '> '


TEMPLATE_EXTENSIONS = '.mako'
