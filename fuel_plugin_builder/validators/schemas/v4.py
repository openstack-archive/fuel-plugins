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

from fuel_plugin_builder.validators.schemas import SchemaV3


COMPONENT_NAME_PATTERN = '^([0-9a-z_-]+:)*[0-9a-z_-]+$'


class SchemaV4(SchemaV3):

    @property
    def package_version(self):
        return {'enum': ['4.0.0']}

    @property
    def component_name(self):
        return {'type': 'string', 'pattern': COMPONENT_NAME_PATTERN}

    @property
    def compatible_names(self):
        return {
            'type': 'array',
            'items': {
                'oneOf': [
                    self.component_name,
                    {'enum': ['*']}
                ]
            }}

    @property
    def components_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
            'items': {
                'required': ['type', 'name'],
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'name': self.component_name,
                    'type': {
                        'enum': [
                            'hypervisor',
                            'network',
                            'storage',
                            'additional_service']},
                    'compatible': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'hypervisors': self.compatible_names,
                            'networks': self.compatible_names,
                            'storages': self.compatible_names,
                            'additional_services': self.compatible_names
                        }
                    }
                }
            }
        }
