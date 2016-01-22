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

from fuel_plugin_builder.validators.schemas import SchemaV4
from fuel_plugin_builder.validators.schemas.v4 import TASK_NAME_PATTERN
from fuel_plugin_builder.validators.schemas.v4 import TASK_ROLE_PATTERN

TASK_VERSION_2_0_PATTERN = '^2.0.0$'


class SchemaV5(SchemaV4):

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
                    'type': 'string', "pattern": TASK_VERSION_2_0_PATTERN},
                #FIXME(ikutukov) do we do alias or renaming roles->role?
                # 'roles': self._task_role,
                'role': self._task_role,
                'cross-depends': {
                    'type': 'array',
                    'items': self._task_relation},
                'cross-depended-by': {
                    'type': 'array',
                    'items': self._task_relation},
                'required_for': self._roles,
                'requires': self._roles,
                'reexecute_on': self._task_reexecute,
                'parameters': parameters or {},
            }
        }

    @property
    def node_roles_schema(self):
        schema = super(SchemaV5, self).node_roles_schema
        schema_pattern = schema['patternProperties']['^[0-9a-zA-Z_-]+$']
        schema_pattern['properties']['tasks'] = {
            'type': 'array',
            'items': {
                'type': 'string',
                'pattern': TASK_ROLE_PATTERN}}
        return schema
