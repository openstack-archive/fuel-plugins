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

import six


class SchemaTaskV2_1_0(object):

    file_permissions_pattern = '^[0-7]{4}$'

    role_aliases = ('roles', 'groups', 'role')
    stage_pattern = '^(post_deployment|pre_deployment)' \
                    '(/[-+]?([0-9]*\.[0-9]+|[0-9]+))?$'
    task_name_pattern = '^[0-9a-zA-Z_-]+$|^\*$'
    task_obligatory_fields = ('id', 'type')
    task_role_pattern = '^[0-9a-zA-Z_-]+$|^\*$'
    task_version_pattern = '^\d+.\d+.\d+$'

    @property
    def _node_resolve_policy(self):
        return {
            'type': 'string',
            'enum': ['all', 'any']
        }

    @property
    def _yaql_expression(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['yaql_exp'],
            'properties': {
                'yaql_exp': {'type': 'string'},
            }
        }

    @property
    def _task_relation(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {
                    'oneOf': [
                        {'type': 'string'},
                        self._yaql_expression],
                },
                'role': {
                    'oneOf': [
                        {'type': 'string'},
                        {'type': 'array'},
                        self._yaql_expression]
                },
                'policy': self._node_resolve_policy,
            }
        }

    @property
    def _task_role(self):
        return {
            'oneOf': [
                {
                    'type': 'string',
                    'format': 'fuel_task_role_format'
                },
                {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'format': 'fuel_task_role_format'
                    }
                }
            ]
        }

    @property
    def _task_strategy(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['type'],
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['parallel', 'one_by_one']},
                'amount': {
                    'oneOf': [
                        {'type': 'integer'},
                        self._yaql_expression
                    ]
                }
            }
        }

    @property
    def _task_stage(self):
        return {'type': 'string', 'pattern': self.stage_pattern}

    @property
    def _task_reexecute(self):
        return {
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': ['deploy_changes']
            }
        }

    @property
    def _task_group(self):
        return {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': self.task_name_pattern
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
        task_specific_req_fields = set(
            self.task_obligatory_fields + (tuple(required) if required else ())
        )
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': task_specific_req_fields,
            'properties': {
                'type': {'enum': task_types},
                'id': {
                    'type': 'string',
                    'pattern': self.task_name_pattern
                },
                'version': {
                    'type': 'string',
                    "pattern": self.task_version_pattern
                },
                'role': self._task_role,
                'groups': self._task_role,
                'roles': self._task_role,
                'required_for': self._task_group,
                'requires': self._task_group,
                'cross-depends': {
                    'oneOf': [
                        {'type': 'array', 'items': self._task_relation},
                        self._yaql_expression]
                },
                'cross-depended-by': {
                    'oneOf': [
                        {'type': 'array', 'items': self._task_relation},
                        self._yaql_expression]
                },
                'stage': self._task_stage,
                'tasks': {  # used only for 'group' tasks
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'pattern': self.task_role_pattern}},
                'reexecute_on': self._task_reexecute,
                'parameters': parameters,
            }
        }

    @property
    def tasks(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': self._gen_task_schema(
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

    @property
    def copy_files_task(self):
        return self._gen_task_schema(
            "copy_files",
            ['parameters'],
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
                        'pattern': self.file_permissions_pattern},
                    'dir_permissions': {
                        'type': 'string',
                        'pattern': self.file_permissions_pattern}}})

    @property
    def group_task(self):
        return self._gen_task_schema(
            "group",
            []
        )

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
            [],
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
        return self._gen_task_schema(
            "skipped"
        )

    @property
    def stage_task(self):
        return self._gen_task_schema(
            "stage"
        )

    @property
    def sync_task(self):
        return self._gen_task_schema(
            "sync",
            ['parameters'],
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
            ['parameters'],
            {
                'type': 'object',
                'required': ['path', 'data'],
                'properties': {
                    'path': {'type': 'string'},
                    'data': {'type': 'string'}
                }
            }
        )


schema_task_v2_1_0 = SchemaTaskV2_1_0()
