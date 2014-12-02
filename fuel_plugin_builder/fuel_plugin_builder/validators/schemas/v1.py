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

PLUGIN_RELEASE_SCHEMA = {
    'type': 'object',
    'required': ['version', 'os', 'mode'],
    'properties': {
        'version': {'type': 'string'},
        'os': {'enum': ['ubuntu', 'centos']},
        'deployment_scripts_path': {'type': 'string'},
        'repository_path': {'type': 'string'},
        'mode': {'type': 'array',
                 'items': {'enum': ['ha', 'multinode']}}}}


METADATA_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'plugin',
    'type': 'object',
    'required': ['name', 'title', 'version', 'releases', 'package_version'],
    'properties': {
        'name': {
            'type': 'string',
            # Only lower case letters, numbers, '_', '-' symbols
            'pattern': '^[a-z0-9_-]+$'},
        'title': {'type': 'string'},
        'version': {'type': 'string'},
        'package_version': {'enum': ['1.0.0']},
        'description': {'type': 'string'},
        'fuel_version': {'type': 'array',
                         'items': {'type': 'string'}},
        'releases': {
            'type': 'array',
            'items': PLUGIN_RELEASE_SCHEMA}}}


POSITIVE_INTEGER = {'type': 'integer', 'minimum': 0}


PUPPET_PARAMETERS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['timeout', 'puppet_modules', 'puppet_manifest'],
    'properties': {
        'timeout': POSITIVE_INTEGER,
        'puppet_modules': {'type': 'string'},
        'puppet_manifest': {'type': 'string'}}}


SHELL_PARAMETERS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['timeout', 'cmd'],
    'properties': {
        'timeout': POSITIVE_INTEGER,
        'cmd': {'type': 'string'}}}


TASK_BASE_PARAMETERS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['timeout'],
    'properties': {
        'timeout': POSITIVE_INTEGER}}


TASK_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['parameters', 'type', 'stage', 'role'],
    'properties': {
        'type': {'enum': ['puppet', 'shell']},
        'parameters': TASK_BASE_PARAMETERS,
        'stage': {'enum': ['post_deployment', 'pre_deployment']},
        'role': {
            'oneOf': [
                {'type': 'array', 'items': {'type': 'string'}},
                {'enum': ['*']}]}}}


TASKS_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'array',
    'items': TASK_SCHEMA}


ATTR_ELEMENT_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'required': ['type', 'label', 'weight', 'value'],
    'properties': {
        'type': {'type': 'string'},
        'weight': {'type': 'integer'},
        'value': {'type': ['string', 'boolean']},
        'label': {'type': 'string'},
        'values': {'type': 'array', 'items':
                   {'type': 'object',
                    'required': ['data', 'label'],
                    'properties': {
                        'data': {'type': 'string'},
                        'label': {'type': 'string'}}}}}}


ATTR_META_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'label': {'type': 'string'},
        'weight': {'type': 'integer'},
        'toggleable': {'type': 'boolean'},
        'enabled': {'type': 'boolean'},
        'restrictions': {
            'type': 'array', 'items': {'type': ['string', 'object']}}}}


ATTR_ROOT_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'attributes': {'type': 'object'}}}
