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

from fuel_plugin_builder import validators


# Tasks have their own versioning line slightly dependant on Nailgun and
# FPB versions.


class SchemaMetadataV5_0_0(object):

    package_version = '5.0.0'

    @property
    def metadata_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'plugin',
            'type': 'object',
            'required': [
                'name',
                'title',
                'version',
                'package_version',
                'description',
                'fuel_version',
                'licenses',
                'authors',
                'homepage',
                'releases',
                'groups'
            ],
            'properties': {
                'name': {
                    'type': 'string',
                    'pattern': validators.schemas.common_v1_0_0.plugin_name_pattern
                },
                'title': {'type': 'string'},
                'version': {'type': 'string'},
                'package_version': self.package_version,
                'description': {'type': 'string'},
                'fuel_version': validators.schemas.common_v1_0_0.list_of_strings,
                'licenses': validators.schemas.common_v1_0_0.list_of_strings,
                'authors': validators.schemas.common_v1_0_0.list_of_strings,
                'groups': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'enum': [
                            'network',
                            'storage',
                            'storage::cinder',
                            'storage::glance',
                            'hypervisor',
                            'monitoring'
                        ]
                    }
                },
                'homepage': {'type': 'string'},
                'releases': {
                    'type': 'array',
                    'items': {  # more detailed check will be at release level
                        'type': 'object'
                    }
                }
            }
        }


metadata_v5_0_0 = SchemaMetadataV5_0_0()
