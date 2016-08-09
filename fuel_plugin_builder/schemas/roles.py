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


from common import common_v1_0_0


class SchemaRolesV3_0_0(object):

    @property
    def roles_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'patternProperties': {
                '^[0-9a-zA-Z_-]+$': {
                    'type': 'object',
                    'required': ['name', 'description'],
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Name that will be shown on UI'},
                        'description': {
                            'type': 'string',
                            'description': ('Short description of role'
                                            ' functionality')},
                        'conflicts': {
                            'oneOf': [
                                common_v1_0_0.list_of_strings,
                                {
                                    'type': 'string',
                                    'enum': ['*']
                                }
                            ]
                        },
                        'has_primary': {
                            'type': 'boolean',
                            'description': ('During orchestration this role'
                                            ' will be splitted into'
                                            ' primary-role and role.')},
                        'public_ip_required': {
                            'type': 'boolean',
                            'description': ('Specify if role needs public'
                                            ' IP address.')},
                        'update_required': common_v1_0_0.list_of_strings,
                        'update_once': common_v1_0_0.list_of_strings,
                        'weight': {
                            'type': 'integer',
                            'description': ('Specify weight that will be'
                                            ' used to sort out the roles'
                                            ' on the Fuel web UI')
                        },
                        'limits': common_v1_0_0.limits,
                        'restrictions': common_v1_0_0.restrictions
                    }
                }
            },
            'additionalProperties': False
        }

roles_v3_0_0 = SchemaRolesV3_0_0()
