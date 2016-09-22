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

from attributes import attributes_v8_0


class SchemaNodeAttributesV9_1(object):

    @property
    def node_attributes(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'patternProperties': {
                '^[0-9a-zA-Z_-]+$': {"$ref": "#/definitions/attrItem"}
            },
            "definitions": {
                "attrItem": self.node_nic_attributes
            },
            "additionalProperties": False
        }

    @property
    def node_nic_attributes(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'metadata': self.node_nic_metadata_items
            },
            'patternProperties': {
                '^(?!metadata)[0-9a-zA-Z_-]+$': self.node_nic_attribute_items
            },
            "additionalProperties": False
        }

    @property
    def node_nic_attribute_items(self):
        return {
            'type': 'object',
            'required': ['type', 'label', 'value'],
            'properties': {
                'label': {'type': 'string'},
                'description': {'type': 'string'},
                'type': {'type': 'string'},
                'value': {},
                'restrictions': attributes_v8_0.restrictions
            }
        }

    @property
    def node_nic_metadata_items(self):
        return {
            'type': 'object',
            'required': ['label'],
            'properties': {
                'label': {'type': 'string'},
                'restrictions': attributes_v8_0.restrictions
            }
        }


node_attributes_v9_1 = SchemaNodeAttributesV9_1()
