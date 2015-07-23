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

from fuel_plugin_builder.validators.schemas import v2


class SchemaV3(v2.SchemaV2):

    @property
    def package_version(self):
        return {'enum': ['3.0.0']}

    @property
    def network_roles_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id', 'default_mapping', 'properties'],
                'properties': {
                    'id': {'type': 'string'},
                    'default_mapping': {'type': 'string'},
                    'properties': {
                        'type': 'object',
                        'required': ['subnet', 'gateway', 'vip'],
                        'properties': {
                            'subnet': {'type': 'boolean'},
                            'gateway': {'type': 'boolean'},
                            'vip': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'required': ['name'],
                                    'properties': {
                                        'name': {
                                            'type': 'string'},
                                        'namespace': {
                                            'type': 'string'}}}}}}}}
        }

    @property
    def task_stage(self):
        return {
            'type': 'string',
            'pattern': '^(post_deployment|pre_deployment)'
                       '(/[-+]?([0-9]*\.[0-9]+|[0-9]+))?$'
        }

    @property
    def task_role(self):
        return {
            'oneOf': [
                self.list_of_strings,
                {'enum': ['*']}
            ]
        }

    @property
    def task_required(self):
        return ['parameters', 'type', 'stage', 'role']

    @property
    def task_schema(self):
        return {
            'oneOf': [
                {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'type': 'object',
                    'required': self.task_required,
                    'properties': {
                        'type': {'enum': ['shell']},
                        'parameters': {
                            'type': 'object',
                            'required': ['timeout', 'cmd'],
                            'additionalProperties': False,
                            'properties': {
                                'timeout': self.positive_integer,
                                'cmd': {'type': 'string'}
                            }
                        },
                        'stage': self.task_stage,
                        'role': self.task_role
                    }
                },
                {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'type': 'object',
                    'required': self.task_required,
                    'properties': {
                        'type': {'enum': ['puppet']},
                        'parameters': {
                            'type': 'object',
                            'required': ['timeout', 'puppet_modules',
                                         'puppet_manifest'],
                            'additionalProperties': False,
                            'properties': {
                                'timeout': self.positive_integer,
                                'puppet_modules': {'type': 'string'},
                                'puppet_manifest': {'type': 'string'}
                            }
                        },
                        'stage': self.task_stage,
                        'role': self.task_role
                    }
                },
                {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'type': 'object',
                    'required': self.task_required,
                    'properties': {
                        'type': {'enum': ['reboot']},
                        'parameters': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'timeout': self.positive_integer,
                            }
                        },
                        'stage': self.task_stage,
                        'role': self.task_role
                    }
                }
            ]
        }
