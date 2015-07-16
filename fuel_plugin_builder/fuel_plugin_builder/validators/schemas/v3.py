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
    def deployment_task_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array'
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
            'type': 'object'
        }

    @property
    def volume_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object'
        }
