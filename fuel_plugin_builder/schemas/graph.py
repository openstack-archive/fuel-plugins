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

from task import task_v2_1_0


class SchemaGraphV9_1(object):
    graph = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'metadata': {'type': 'object'},
            'name': {'type': 'string'},
            'tasks': task_v2_1_0.tasks
        }
    }

    @property
    def graph_association(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
            'required': ['graph'],
            'properties': {
                'graph': self.graph,
                'type': {'type': 'string'}
            }
        }


graph_v9_1 = SchemaGraphV9_1()
