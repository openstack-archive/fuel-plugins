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


class BaseSchema(object):

    @property
    def plugin_release_schema(self):
        return {
            'type': 'object',
            'required': ['version', 'os', 'mode'],
            'properties': {
                'version': {'type': 'string'},
                'os': {'enum': ['ubuntu', 'centos']},
                'deployment_scripts_path': {'type': 'string'},
                'repository_path': {'type': 'string'},
                'mode': {'type': 'array',
                         'items': {'enum': ['ha', 'multinode']}}}
        }

    @property
    def metadata_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'plugin',
            'type': 'object',
            'required': [
                'name',
                'title',
                'version',
                'package_version',
                'description',
                'fuel_version',
                'releases',
            ],
            'properties': {
                'name': {
                    'type': 'string',
                    # Only lower case letters, numbers, '_', '-' symbols
                    'pattern': '^[a-z0-9_-]+$'},
                'title': {'type': 'string'},
                'version': {'type': 'string'},
                'package_version': {'enum': ['1.0.0']},
                'description': {'type': 'string'},
                'fuel_version': self.list_of_strings,
                'releases': {
                    'type': 'array',
                    'items': self.plugin_release_schema}}
        }

    @property
    def list_of_strings(self):
        return {'type': 'array',
                'items': {'type': 'string'}}

    @property
    def positive_integer(self):
        return {'type': 'integer', 'minimum': 0}

    @property
    def puppet_parameters(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['timeout', 'puppet_modules', 'puppet_manifest'],
            'properties': {
                'timeout': self.positive_integer,
                'puppet_modules': {'type': 'string'},
                'puppet_manifest': {'type': 'string'}}
        }

    @property
    def shell_parameters(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['timeout', 'cmd'],
            'properties': {
                'timeout': self.positive_integer,
                'cmd': {'type': 'string'}}
        }

    @property
    def task_base_parameters(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['timeout'],
            'properties': {
                'timeout': self.positive_integer}
        }

    @property
    def task_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['parameters', 'type', 'stage', 'role'],
            'properties': {
                'type': {'enum': ['puppet', 'shell']},
                'parameters': self.task_base_parameters,
                'stage': {'enum': ['post_deployment', 'pre_deployment']},
                'role': {
                    'oneOf': [
                        self.list_of_strings,
                        {'enum': ['*']}]}}
        }

    @property
    def tasks_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': self.task_schema
        }

    @property
    def attr_element_schema(self):
        return {
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
                                'label': {'type': 'string'}}}}}
        }

    @property
    def attr_meta_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'weight': {'type': 'integer'},
                'toggleable': {'type': 'boolean'},
                'enabled': {'type': 'boolean'},
                'restrictions': {
                    'type': 'array', 'items': {'type': ['string', 'object']}}}
        }

    @property
    def attr_root_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'attributes': {'type': 'object'}}
        }
