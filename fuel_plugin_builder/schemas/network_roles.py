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


class SchemaNetworkRolesV7_0(object):
    _network_role_pattern = '^[0-9a-z_-]+$'

    @property
    def _vip(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['name'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'pattern': self._network_role_pattern
                    },
                    'namespace': {
                        'type': 'string',
                        'pattern': self._network_role_pattern
                    }
                }
            }
        }

    @property
    def schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'required': [
                    'id',
                    'default_mapping',
                    'properties'
                ],
                'properties': {
                    'id': {
                        'type': 'string'
                    },
                    'default_mapping': {
                        'type': 'string'
                    },
                    'properties': {
                        'type': 'object',
                        'required': ['subnet', 'gateway', 'vip'],
                        'properties': {
                            'subnet': {
                                'type': 'boolean'
                            },
                            'gateway': {
                                'type': 'boolean'
                            },
                            'vip': self._vip
                        }
                    }
                }
            }
        }


class SchemaNetworkRolesV8_0(object):
    _network_role_pattern = '^[0-9a-z_-]+$'

    _vip = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            'name': {
                'type': 'string',
                'pattern': _network_role_pattern
            },
            'namespace': {
                'type': 'string',
                'pattern': _network_role_pattern
            }
        }
    }

    _vips = {
        'type': 'array',
        'items': _vip
    }

    @property
    def schema(self):
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
                            'vip': self._vips
                        }
                    }
                }
            }
        }


network_roles_v7_0 = SchemaNetworkRolesV7_0()
network_roles_v8_0 = SchemaNetworkRolesV8_0()
