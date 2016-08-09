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

import utils

from fuel_plugin_builder.validators.schemas import SchemaV3


COMPONENTS_TYPES_STR = '|'.join(
    ['hypervisor', 'network', 'storage', 'additional_service'])
COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*[0-9a-z_-]+$'.format(COMPONENTS_TYPES_STR)
COMPATIBLE_COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*([0-9a-z_-]+|(\*)?)$'.format(COMPONENTS_TYPES_STR)


TASK_NAME_PATTERN = TASK_ROLE_PATTERN = '^[0-9a-zA-Z_-]+$|^\*$'
NETWORK_ROLE_PATTERN = '^[0-9a-z_-]+$'
FILE_PERMISSIONS_PATTERN = '^[0-7]{4}$'
TASK_VERSION_PATTERN = '^\d+.\d+.\d+$'
STAGE_PATTERN = '^(post_deployment|pre_deployment)' \
                '(/[-+]?([0-9]*\.[0-9]+|[0-9]+))?$'

ROLE_ALIASES = ('roles', 'groups', 'role')
TASK_OBLIGATORY_FIELDS = ['id', 'type']
ROLELESS_TASKS = ('stage')


class SchemaV4(SchemaV3):


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
                    {'type': 'object',
                     'properties': {'generator': {'type': 'string'}}}
                ]},
                'label': {'type': 'string'},
                'restrictions': self.restrictions,
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
                'restrictions': self.restrictions}
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
        schema = utils.make_schema(
            required_fields=[],
            properties={
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
        )

        return schema

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
                        'pattern': COMPATIBLE_COMPONENT_NAME_PATTERN
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
                        'pattern': COMPONENT_NAME_PATTERN
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