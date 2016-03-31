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

from fuel_plugin_builder.validators.schemas import SchemaV2


TASK_NAME_PATTERN = '^[0-9a-zA-Z_-]+$'
NETWORK_ROLE_PATTERN = '^[0-9a-z_-]+$'
FILE_PERMISSIONS_PATTERN = '^[0-7]{4}$'


class SchemaV3(SchemaV2):

    @property
    def task_role(self):
        return {
            'oneOf': [
                self.task_group,
                {'enum': ['*', 'master']}
            ]
        }

    @property
    def task_group(self):
        return {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': TASK_NAME_PATTERN
            }
        }

    @property
    def rule(self):
        return {
            'type': ['string', 'integer']
        }

    @property
    def override(self):
        return {
            'type': 'object',
            'description': 'Property which can change limit recommended|min'
                           '|max properties due to some additional condition',
            'required': ['condition'],
            'properties': {
                'condition': {'type': 'string'},
                'max': self.rule,
                'recommended': self.rule,
                'min': self.rule,
                'message': {'type': 'string'}
            }
        }

    @property
    def overrides(self):
        return {
            'type': 'array',
            'description': 'Array of limit override properties',
            'minItems': 1,
            'items': self.override
        }

    @property
    def limits(self):
        return {
            'type': 'object',
            'description': 'Limits for count of nodes for node role',
            'properties': {
                'condition': self.condition,
                'max': self.rule,
                'recommended': self.rule,
                'min': self.rule,
                'overrides': self.overrides
            }
        }

    @property
    def package_version(self):
        return {'enum': ['3.0.0']}

    @property
    def puppet_task(self):
        return {
            'type': 'object',
            'properties': {
                'type': {'enum': ['puppet']},
                'groups': self.task_group,
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'required': [
                        'puppet_manifest', 'puppet_modules', 'timeout'],
                    'properties': {
                        'puppet_manifest': {
                            'type': 'string',
                            'minLength': 1},
                        'puppet_modules': {
                            'type': 'string',
                            'minLength': 1},
                        'timeout': {
                            'type': 'integer'},
                        'retries': {
                            'type': 'integer'},
                    }
                }
            }
        }

    @property
    def shell_task(self):
        return {
            'type': 'object',
            'required': ['role'],
            'properties': {
                'type': {'enum': ['shell']},
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'required': ['cmd'],
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
    def group_task(self):
        return {
            'type': 'object',
            'required': ['role'],
            'properties': {
                'type': {'enum': ['group']},
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'strategy': {
                            'type': 'object',
                            'properties': {
                                'type': {
                                    'enum': ['parallel', 'one_by_one']}}}}}}
        }

    @property
    def skipped_task(self):
        return {
            'type': 'object',
            'properties': {
                'type': {'enum': ['skipped']}}
        }

    @property
    def copy_files(self):
        return {
            'type': 'object',
            'required': ['role', 'parameters'],
            'properties': {
                'type': {'enum': ['copy_files']},
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'required': ['files'],
                    'properties': {
                        'files': {
                            'type': 'array',
                            'minItems': 1,
                            'items': {
                                'type': 'object',
                                'required': ['src', 'dst'],
                                'properties': {
                                    'src': {'type': 'string'},
                                    'dst': {'type': 'string'}}}},
                        'permissions': {
                            'type': 'string',
                            'pattern': FILE_PERMISSIONS_PATTERN},
                        'dir_permissions': {
                            'type': 'string',
                            'pattern': FILE_PERMISSIONS_PATTERN}}}}
        }

    @property
    def sync(self):
        return {
            'type': 'object',
            'required': ['role', 'parameters'],
            'properties': {
                'type': {'enum': ['sync']},
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'required': ['src', 'dst'],
                    'properties': {
                        'src': {'type': 'string'},
                        'dst': {'type': 'string'},
                        'timeout': {'type': 'integer'}}}}
        }

    @property
    def upload_file(self):
        return {
            'type': 'object',
            'required': ['role', 'parameters'],
            'properties': {
                'type': {'enum': ['upload_file']},
                'role': self.task_role,
                'parameters': {
                    'type': 'object',
                    'required': ['path', 'data'],
                    'properties': {
                        'path': {'type': 'string'},
                        'data': {'type': 'string'}}}}
        }

    @property
    def stage(self):
        return {
            'type': 'object',
            'properties': {
                'type': {'enum': ['stage']}}
        }

    @property
    def reboot(self):
        return {
            'type': 'object',
            'properties': {
                'type': {'enum': ['reboot']},
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'timeout': {'type': 'integer'}}}}
        }

    @property
    def deployment_task_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['id', 'type'],
                'properties': {
                    'id': {
                        'type': 'string',
                        'pattern': TASK_NAME_PATTERN},
                    'type': {
                        'enum': [
                            'puppet',
                            'shell',
                            'group',
                            'skipped',
                            'copy_files',
                            'sync',
                            'upload_file',
                            'stage',
                            'reboot']},
                    'required_for': self.task_group,
                    'requires': self.task_group}}
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
                                            'type': 'string',
                                            'pattern': NETWORK_ROLE_PATTERN},
                                        'namespace': {
                                            'type': 'string',
                                            'pattern': NETWORK_ROLE_PATTERN}
                                    }}}}}}}
        }

    @property
    def node_roles_schema(self):
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
                                self.list_of_strings,
                                {'type': 'string', 'enum': ['*']}]},
                        'has_primary': {
                            'type': 'boolean',
                            'description': ('During orchestration this role'
                                            ' will be splitted into'
                                            ' primary-role and role.')},
                        'public_ip_required': {
                            'type': 'boolean',
                            'description': ('Specify if role needs public'
                                            ' IP address.')},
                        'update_required': self.list_of_strings,
                        'update_once': self.list_of_strings,
                        'weight': {
                            'type': 'integer',
                            'description': ('Specify weight that will be'
                                            ' used to sort out the roles'
                                            ' on the Fuel web UI')},
                        'limits': self.limits,
                        'restrictions': self.restrictions}}},
            'additionalProperties': False
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
                        TASK_NAME_PATTERN: {
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
                                    'id': {'type': 'string'}}}}},
                    'additionalProperties': False},
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

    @property
    def task_base_parameters(self):
        schema = super(SchemaV3, self).task_base_parameters
        schema['properties']['retries'] = self.positive_integer
        return schema
