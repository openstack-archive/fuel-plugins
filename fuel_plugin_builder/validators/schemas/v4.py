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

import six

from fuel_plugin_builder.validators.schemas import SchemaV3


COMPONENTS_TYPES_STR = '|'.join(
    ['hypervisor', 'network', 'storage', 'additional_service'])
COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*[0-9a-z_-]+$'.format(COMPONENTS_TYPES_STR)
COMPATIBLE_COMPONENT_NAME_PATTERN = \
    '^({0}):([0-9a-z_-]+:)*([0-9a-z_-]+|(\*)?)$'.format(COMPONENTS_TYPES_STR)


TASK_NAME_PATTERN = TASK_ROLE_PATTERN = '^[0-9a-zA-Z_-]+$'
NETWORK_ROLE_PATTERN = '^[0-9a-z_-]+$'
FILE_PERMISSIONS_PATTERN = '^[0-7]{4}$'
TASK_VERSION_PATTERN = '^\d+.\d+.\d+$'
STAGE_PATTERN = '^(post_deployment|pre_deployment)' \
                '(/[-+]?([0-9]*\.[0-9]+|[0-9]+))?$'


class SchemaV4(SchemaV3):

    @property
    def _task_relation(self):
        return {
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string'},
                'role': self._task_role,
                'policy': {
                    'type': 'string',
                    'enum': ['all', 'any']
                }
            }
        }

    @property
    def _task_role(self):
        return {
            'oneOf': [
                {
                    'type': 'string',
                    'enum': ['*', 'master', 'self']
                },
                {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': TASK_ROLE_PATTERN
                    }
                }
            ]
        }

    @property
    def _task_strategy(self):
        return {
            'type': 'object',
            'properties': {
                'type': {
                    'enum': ['parallel', 'one_by_one']
                }
            }
        }

    @property
    def _task_stage(self):
        return {'type': 'string', 'pattern': STAGE_PATTERN}

    @property
    def _task_reexecute(self):
        return {
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': ['deploy_changes']
            }
        }

    def _gen_task_schema(self, task_types, required=None, parameters=None):
        """Generate deployment task schema using prototype.

        :param task_types: task types
        :type task_types: str|list
        :param required: new required fields
        :type required: list
        :param parameters: new properties dict
        :type parameters: dict
        :return:
        :rtype: dict
        """
        if not task_types:
            raise ValueError('Task type should not be empty')

        if isinstance(task_types, six.string_types):
            task_types = [task_types]

        # patch strategy parameter
        parameters = parameters or {
            "type": "object",
        }
        parameters.setdefault("properties", {})
        parameters["properties"].setdefault("strategy", self._task_strategy)

        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': list(set(['id', 'type'] + (required or []))),
            'properties': {
                'type': {'enum': task_types},
                'id': {
                    'type': 'string',
                    'pattern': TASK_NAME_PATTERN},
                'version': {
                    'type': 'string', "pattern": TASK_VERSION_PATTERN},
                'role': self._task_role,
                'required_for': self.task_group,
                'requires': self.task_group,
                'cross-depends': {
                    'type': 'array',
                    'items': self._task_relation},
                'cross-depended-by': {
                    'type': 'array',
                    'items': self._task_relation},
                'stage': self._task_stage,
                'tasks': {  # used only for 'group' tasks
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': TASK_ROLE_PATTERN}},
                'reexecute_on': self._task_reexecute,
                'parameters': parameters or {},
            }
        }

    @property
    def deployment_task_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                "$ref": "#/definitions/anyTask"
            },
            "definitions": {
                "anyTask": self._gen_task_schema(
                    [
                        'copy_files',
                        'group',
                        'reboot',
                        'shell',
                        'skipped',
                        'stage',
                        'sync',
                        'puppet',
                        'upload_file',
                    ]
                )
            }
        }

    @property
    def copy_files_task(self):
        return self._gen_task_schema(
            "copy_files",
            ['role', 'parameters'],
            {
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
                        'pattern': FILE_PERMISSIONS_PATTERN}}})

    @property
    def group_task(self):
        return self._gen_task_schema("group", ['role'])

    @property
    def puppet_task(self):
        return self._gen_task_schema(
            "puppet",
            [],
            {
                'type': 'object',
                'required': [
                    'puppet_manifest', 'puppet_modules', 'timeout'],
                'properties': {
                    'puppet_manifest': {
                        'type': 'string', 'minLength': 1},
                    'puppet_modules': {
                        'type': 'string', 'minLength': 1},
                    'timeout': {'type': 'integer'},
                    'retries': {'type': 'integer'}
                }
            }
        )

    @property
    def reboot_task(self):
        return self._gen_task_schema(
            "reboot",
            [],
            {
                'type': 'object',
                'properties': {
                    'timeout': {'type': 'integer'}
                }
            }
        )

    @property
    def shell_task(self):
        return self._gen_task_schema(
            "shell",
            ['role'],
            {
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
                        'type': 'integer'}
                }
            }
        )

    @property
    def skipped_task(self):
        return self._gen_task_schema("skipped")

    @property
    def stage_task(self):
        return self._gen_task_schema("stage")

    @property
    def sync_task(self):
        return self._gen_task_schema(
            "sync",
            ['role', 'parameters'],
            {
                'type': 'object',
                'required': ['src', 'dst'],
                'properties': {
                    'src': {'type': 'string'},
                    'dst': {'type': 'string'},
                    'timeout': {'type': 'integer'}
                }
            }
        )

    @property
    def upload_file_task(self):
        return self._gen_task_schema(
            "upload_file",
            ['role', 'parameters'],
            {
                'type': 'object',
                'required': ['path', 'data'],
                'properties': {
                    'path': {'type': 'string'},
                    'data': {'type': 'string'}
                }
            }
        )

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
    def attr_root_schema(self):
        schema = super(SchemaV4, self).attr_root_schema
        schema['properties']['attributes']['properties'] = {
            'metadata': {
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
