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

from fuel_plugin_builder.validators.schemas.v2 import SchemaV2


class SchemaV3(SchemaV2):

    @property
    def package_version(self):
        return {'enum': ['3.0.0']}

    @property
    def puppet_task(self):
        return {
            'type': 'object',
            'required': ['id', 'type', 'groups'],
            'properties': {
                'id': {
                    'type': 'string',
                    'pattern': '^[0-9a-zA-Z_-]+$'},
                'type': {
                    'type': 'string',
                    'pattern': 'puppet'},
                'groups': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'required_for': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'requires': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'parameters': {
                    'required': ['puppet_manifest', 'puppet_modules'],
                    'properties': {
                        'puppet_manifest': {
                            'type': 'string'},
                        'puppet_modules': {
                            'type': 'string'},
                        'timeout': {
                            'type': 'integer'}}}}
        }

    @property
    def shell_or_group_task(self):
        return {
            'type': 'object',
            'required': ['id', 'type', 'role'],
            'properties': {
                'id': {
                    'type': 'string',
                    'pattern': '^[0-9a-zA-Z_-]+$'},
                'type': {
                    'type': 'string',
                    'pattern': 'shell|group'},
                'role': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'required_for': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'requires': {
                    'type': 'string',
                    'pattern': '^[[0-9a-zA-Z_-]+]$'},
                'parameters': {
                    'properties': {
                        'cmd': {
                            'type': 'string'},
                        'retries': {
                            'type': 'integer'},
                        'interval': {
                            'type': 'integer'},
                        'timeout': {
                            'type': 'integer'}}}}
        }

    @property
    def deployment_task_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'oneOf': [
                    self.puppet_task,
                    self.shell_or_group_task
                ]}
        }

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
    def node_role_schema(self):
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
                            'type': 'array',
                            'description': ('Specify which roles conflict'
                                            ' this one.')},
                        'has_primary': {
                            'type': 'boolean',
                            'description': ('During orchestration this role'
                                            ' will be splitted into'
                                            ' primary-role and role.')},
                        'public_ip_required': {
                            'type': 'boolean',
                            'description': ('Specify if role needs public'
                                            ' IP address.')},
                        'update_required': {
                            'type': 'array',
                            'description': ('Specified roles will be selected'
                                            ' for deployment, when a current'
                                            ' role is selected.')},
                        'update_once': {
                            'type': 'array',
                            'description': ('Specified roles will be updated'
                                            ' if current role added to'
                                            ' cluster first time.')},
                        'weight': {
                            'type': 'integer',
                            'description': ('Specify weight that will be'
                                            ' used to sort out the roles'
                                            ' on the Fuel web UI')},
                        'limits': self.limits,
                        'restrictions': self.restrictions}}}
        }

    @property
    def volume_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['volumes_roles_mapping', 'volumes'],
            'properties': {
                'volumes_roles_mapping': {
                    'type': 'object',
                    'patternProperties': {
                        '^[0-9a-zA-Z_-]+$': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'description': 'Volume allocations for role',
                                'required': ['allocate_size', 'id'],
                                'properties': {
                                    'allocate_size': {
                                        'type': 'string',
                                        'enum': ['all', 'min', 'full-disk']},
                                    'id': {'type': 'string'}}}}}},
                'volumes': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['id', 'type'],
                        'properties': {
                            'id': {
                                'type': 'string'},
                            'type': {
                                'type': 'string'}}}}}
        }
