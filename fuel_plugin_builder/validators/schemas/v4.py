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

from fuel_plugin_builder.validators.schemas import SchemaV3


COMPONENTS_TYPES_STR = '|'.join(
    ['hypervisor', 'network', 'storage', 'additional_service'])
COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*[0-9a-z_-]+$'.format(COMPONENTS_TYPES_STR)
COMPATIBLE_COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*([0-9a-z_-]+|(\*)?)$'.format(COMPONENTS_TYPES_STR)


class SchemaV4(SchemaV3):

    @property
    def package_version(self):
        return {'enum': ['4.0.0']}

    @property
    def metadata_schema(self):
        schema = super(SchemaV4, self).metadata_schema
        schema['required'].append('is_hotpluggable')
        schema['properties']['is_hotpluggable'] = {'type': 'boolean'}
        schema['properties']['groups']['items']['enum'].append('equipment')
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
                    'incompatible': self.components_items
                }
            }
        }
