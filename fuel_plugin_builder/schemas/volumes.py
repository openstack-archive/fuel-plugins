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

from task import task_v2_1_0


class SchemaVolumesV7_0(object):
    @property
    def volume(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['volumes_roles_mapping', 'volumes'],
            'properties': {
                'volumes_roles_mapping': {
                    'type': 'object',
                    'patternProperties': {
                        task_v2_1_0.task_name_pattern: {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'description': 'Volume allocations for role',
                                'required': ['allocate_size', 'id'],
                                'properties': {
                                    'allocate_size': {
                                        'type': 'string',
                                        'enum': ['all', 'min', 'full-disk']
                                    },
                                    'id': {'type': 'string'}
                                }
                            }
                        }
                    },
                    'additionalProperties': False
                },
                'volumes': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['id', 'type'],
                        'properties': {
                            'id': {
                                'type': 'string'
                            },
                            'type': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }


volumes_v7_0 = SchemaVolumesV7_0()
