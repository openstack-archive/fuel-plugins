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

from common import common_v6_0


class SchemaNodeRolesV7_0(object):
    @property
    def _rule(self):
        return {
            'type': ['string', 'integer']
        }

    @property
    def _override(self):
        return {
            'type': 'object',
            'description': 'Property which can change limit recommended|min'
                           '|max properties due to some additional condition',
            'required': ['condition'],
            'properties': {
                'condition': {'type': 'string'},
                'max': self._rule,
                'recommended': self._rule,
                'min': self._rule,
                'message': {'type': 'string'}
            }
        }

    @property
    def _overrides(self):
        return {
            'type': 'array',
            'description': 'Array of limit override properties',
            'minItems': 1,
            'items': self._override
        }

    @property
    def _condition(self):
        return {'type': 'string'}

    @property
    def _limits(self):
        return {
            'type': 'object',
            'description': 'Limits for count of nodes for node role',
            'properties': {
                'condition': self._condition,
                'max': self._rule,
                'recommended': self._rule,
                'min': self._rule,
                'overrides': self._overrides
            }
        }

    @property
    def _full_restriction(self):
        return {
            'type': 'object',
            'required': ['condition'],
            'properties': {
                'condition': self._condition,
                'message': {'type': 'string'},
                'action': {'type': 'string'}}}

    @property
    def _short_restriction(self):
        return {
            'type': 'object',
            'minProperties': 1,
            'maxProperties': 1}

    @property
    def _restrictions(self):
        return {
            'type': 'array',
            'minItems': 1,
            'items': {
                'anyOf': [
                    self._condition,
                    self._full_restriction,
                    self._short_restriction]}}

    @property
    def schema(self):
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
                                common_v6_0.list_of_strings,
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
                        'update_required': common_v6_0.list_of_strings,
                        'update_once': common_v6_0.list_of_strings,
                        'weight': {
                            'type': 'integer',
                            'description': ('Specify weight that will be'
                                            ' used to sort out the roles'
                                            ' on the Fuel web UI')
                        },
                        'limits': self._limits,
                        'restrictions': self._restrictions
                    }
                }
            },
            'additionalProperties': False
        }


node_roles_v7_0 = SchemaNodeRolesV7_0()
