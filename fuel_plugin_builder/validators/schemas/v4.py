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


class SchemaV4(SchemaV3):

    @property
    def package_version(self):
        return {'enum': ['4.0.0']}

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
