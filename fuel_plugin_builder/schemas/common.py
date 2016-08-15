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

from fuel_plugin_builder import consts


class SchemaCommonV1_0_0(object):

    @property
    def plugin_name_pattern(self):
        return consts.PLUGIN_NAME_PATTERN

    @property
    def condition(self):
        return {'type': 'string'}

    @property
    def full_restriction(self):
        return {
            'type': 'object',
            'required': ['condition'],
            'properties': {
                'condition': self.condition,
                'message': {'type': 'string'},
                'action': {'type': 'string'}}}

    @property
    def short_restriction(self):
        return {
            'type': 'object',
            'minProperties': 1,
            'maxProperties': 1}

    @property
    def restrictions(self):
        return {
            'type': 'array',
            'minItems': 1,
            'items': {
                'anyOf': [
                    self.condition,
                    self.full_restriction,
                    self.short_restriction]}}

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
                        {'enum': ['*', 'master']}]}}
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
                'value': {'anyOf': [
                    {'type': 'string'},
                    {'type': 'boolean'},
                    {
                        'type': 'object',
                        'properties': {
                            'generator': {'type': 'string'}
                        }
                    }
                ]},
                'label': {'type': 'string'},
                'restrictions': self.restrictions,
                'values': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['data', 'label'],
                        'properties': {
                            'data': {'type': 'string'},
                            'label': {'type': 'string'}
                        }
                    }
                }
            }
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
                'restrictions': self.restrictions
            }
        }

    @property
    def attr_root_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'attributes': {'type': 'object'}
            }
        }

common_v1_0_0 = SchemaCommonV1_0_0()
