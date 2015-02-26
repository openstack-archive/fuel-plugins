# -*- coding: utf-8 -*-

#    Copyright 2014 Mirantis, Inc.
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

from base import BaseSchema


class SchemaV2(BaseSchema):

    metadata_schema = {
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
        ],
        'properties': {
            'name': {
                'type': 'string',
                # Only lower case letters, numbers, '_', '-' symbols
                'pattern': '^[a-z0-9_-]+$'},
            'title': {'type': 'string'},
            'version': {'type': 'string'},
            'package_version': {'enum': ['2.0.0']},
            'description': {'type': 'string'},
            'fuel_version': BaseSchema.list_of_strings,
            'licenses': BaseSchema.list_of_strings,
            'authors': BaseSchema.list_of_strings,
            'homepage': {'type': 'string'},
            'releases': {
                'type': 'array',
                'items': BaseSchema.plugin_release_schema}}
    }

    task_schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'required': ['parameters', 'type', 'stage', 'role'],
        'properties': {
            'type': {'enum': ['puppet', 'shell', 'reboot']},
            'parameters': BaseSchema.task_base_parameters,
            'stage': {'enum': ['post_deployment', 'pre_deployment']},
            'role': {
                'oneOf': [
                    BaseSchema.list_of_strings,
                    {'enum': ['*']}]}}
    }

    reboot_parameters = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'required': ['timeout'],
        'properties': {
            'timeout': BaseSchema.positive_integer}
    }
