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


class SchemaAttributesV4_0_0(object):

    components_types_str = \
        '|'.join(['hypervisor', 'network', 'storage', 'additional_service'])

    component_name_pattern = \
        '^({0}):([0-9a-z_-]+:)*[0-9a-z_-]+$'.format(
            components_types_str)

    compatible_component_name_pattern = \
        '^({0}):([0-9a-z_-]+:)*([0-9a-z_-]+|(\*)?)$'.format(
            components_types_str)

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
                'action': {'type': 'string'}
            }
        }

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
                    self.short_restriction
                ]
            }
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
                        'properties': {'generator': {'type': 'string'}}
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

    @property
    def attr_root_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': [],
            'properties': {
                'attributes': {
                    'type': 'object',
                    'properties': {
                        'group': {
                            'enum': [
                                'general', 'security',
                                'compute', 'network',
                                'storage', 'logging',
                                'openstack_services', 'other'
                            ]
                        }
                    }
                }
            }
        }

    @property
    def components_items(self):
        return {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'pattern': self.compatible_component_name_pattern
                    },
                    'message': {'type': 'string'}
                }
            }
        }

    @property
    def components_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'required': ['name', 'label'],
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'name': {
                        'type': 'string',
                        'pattern': self.component_name_pattern
                    },
                    'label': {'type': 'string'},
                    'description': {'type': 'string'},
                    'compatible': self.components_items,
                    'requires': self.components_items,
                    'incompatible': self.components_items,
                    'bind': {'type': 'array'}
                }
            }
        }


attributes_v4_0_0 = SchemaAttributesV4_0_0()
