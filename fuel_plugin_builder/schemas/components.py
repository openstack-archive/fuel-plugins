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


class SchemaComponentsV4_0_0(object):

    components_types_str = '|'.join([
        'additional_service'
        'hypervisor',
        'network',
        'storage',
    ])

    component_name_pattern = '^({0}):([0-9a-z_-]+:)*[0-9a-z_-]+$'.format(
        components_types_str
    )

    compatible_component_name_pattern = '|'.join([
        component_name_pattern,
        '^(\*)?)$'
    ])

    @property
    def _components_items(self):
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
                    'compatible': self._components_items,
                    'requires': self._components_items,
                    'incompatible': self._components_items,
                    'bind': {'type': 'array'}
                }
            }
        }

components_v4_0_0 = SchemaComponentsV4_0_0()
