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
from release import release_v6_0


# Tasks have their own versioning line slightly dependant on Nailgun and
# FPB versions.


class SchemaMetadataV6_0(object):
    _package_version = {'enum': ['1.0.0']}

    @property
    def schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'plugin',
            'type': 'object',
            'required': ['name', 'title', 'version', 'releases',
                         'package_version'],
            'properties': {
                'name': {
                    'type': 'string',
                    # Only lower case letters, numbers, '_', '-' symbols
                    'pattern': '^[a-z0-9_-]+$'},
                'title': {'type': 'string'},
                'version': {'type': 'string'},
                'package_version': self._package_version,
                'description': {'type': 'string'},
                'fuel_version': {'type': 'array',
                                 'items': {'type': 'string'}},
                'releases': {
                    'type': 'array',
                    'items': release_v6_0.schema}}}


class SchemaMetadataV6_1(object):
    _plugin_name_pattern = '^[a-z0-9_-]+$'
    _package_version = {'enum': ['2.0.0']}

    @property
    def schema(self):
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
                'groups'],
            'properties': {
                'name': {
                    'type': 'string',
                    'pattern': self._plugin_name_pattern},
                'title': {
                    'type': 'string'},
                'version': {
                    'type': 'string'},
                'package_version': self._package_version,
                'description': {
                    'type': 'string'},
                'fuel_version': common_v6_0.list_of_strings,
                'licenses': common_v6_0.list_of_strings,
                'authors': common_v6_0.list_of_strings,
                'groups': {
                    'type': 'array',
                    'uniqueItems': True, 'items':
                        {
                            'enum':
                                [
                                    'network',
                                    'storage',
                                    'storage::cinder',
                                    'storage::glance',
                                    'hypervisor']}},
                'homepage': {
                    'type': 'string'},
                'releases': {
                    'type': 'array',
                    'items': release_v6_0.release}}
        }


class SchemaMetadataV7_0(SchemaMetadataV6_1):
    _package_version = {'enum': ['3.0.0']}


class SchemaMetadataV8_0(SchemaMetadataV7_0):
    _package_version = {'enum': ['4.0.0']}

    @property
    def schema(self):
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
                'groups',
                'is_hotpluggable'],
            'properties': {
                'name': {
                    'type': 'string',
                    'pattern': self._plugin_name_pattern},
                'title': {
                    'type': 'string'},
                'version': {
                    'type': 'string'},
                'package_version': self._package_version,
                'description': {
                    'type': 'string'},
                'fuel_version': common_v6_0.list_of_strings,
                'licenses': common_v6_0.list_of_strings,
                'authors': common_v6_0.list_of_strings,
                'groups': {
                    'type': 'array',
                    'uniqueItems': True, 'items':
                        {
                            'enum':
                                [
                                    'network',
                                    'storage',
                                    'storage::cinder',
                                    'storage::glance',
                                    'hypervisor',
                                    'equipment'
                                ]}},
                'homepage': {
                    'type': 'string'},
                'releases': {
                    'type': 'array',
                    'items': release_v6_0.release},
                'is_hotpluggable': {'type': 'boolean'}}
        }


class SchemaMetadataV9_1(object):
    _package_version = {'enum': ['5.0.0']}
    _plugin_name_pattern = '^[a-z0-9_-]+$'

    @property
    def schema(self):
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
                    'pattern': common_v6_0.plugin_name_pattern
                },
                'title': {'type': 'string'},
                'version': {'type': 'string'},
                'package_version': self._package_version,
                'description': {'type': 'string'},
                'fuel_version': common_v6_0.list_of_strings,
                'licenses': common_v6_0.list_of_strings,
                'authors': common_v6_0.list_of_strings,
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


metadata_v6_0 = SchemaMetadataV6_0()
metadata_v6_1 = SchemaMetadataV6_1()
metadata_v7_0 = SchemaMetadataV7_0()
metadata_v8_0 = SchemaMetadataV8_0()
metadata_v9_1 = SchemaMetadataV9_1()
