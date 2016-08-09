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


# Tasks have their own versioning line slightly dependant on Nailgun and
# FPB versions.

class SchemaReleaseV6_0(object):
    @property
    def release(self):
        return {
            'type': 'object',
            'required': ['version', 'os', 'mode'],
            'properties': {
                'version': {'type': 'string'},
                'os': {'enum': ['ubuntu', 'centos']},
                'deployment_scripts_path': {'type': 'string'},
                'repository_path': {'type': 'string'},
                'mode': {'type': 'array',
                         'items': {'enum': ['ha', 'multinode']}}}}


class SchemaReleaseV9_1(object):
    @property
    def release(self):
        return {
            'type': 'object',
            'required': ['version', 'os', 'mode'],
            'properties': {
                'version': {'type': 'string'},
                'os': {'enum': ['ubuntu', 'centos']},
                'deployment_scripts_path': {'type': 'string'},
                'repository_path': {'type': 'string'},
                'mode': {
                    'type': 'array',
                    'items': {'enum': ['ha', 'multinode']}
                }
            }
        }


release_v6_0 = SchemaReleaseV6_0()
release_v9_1 = SchemaReleaseV9_1()
