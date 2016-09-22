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


class EnvConfigSchemaV6_0(object):
    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'attributes': {
                'type': 'object',
                'additionalProperties': {
                    'type': 'object',
                    'properties': {
                        'type': {'type': 'string'},
                        'weight': {'type': 'integer'},
                        'value': {'type': ['string', 'boolean']},
                        'label': {'type': 'string'}}}}}}


class AttrElementsSchemaV6_0(object):
    attr_element = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'required': ['type', 'label', 'weight', 'value'],
        'properties': {
            'type': {'type': 'string'},
            'weight': {'type': 'integer'},
            'value': {'type': ['string', 'boolean']},
            'label': {'type': 'string'},
            'values': {'type': 'array', 'items': {
                'type': 'object',
                'required': ['data', 'label'],
                'properties': {
                    'data': {'type': 'string'},
                    'label': {'type': 'string'}}}}}}

    attr_meta = {'$schema': 'http://json-schema.org/draft-04/schema#',
                 'type': 'object',
                 'properties': {
                     'label': {'type': 'string'},
                     'weight': {'type': 'integer'},
                     'toggleable': {'type': 'boolean'},
                     'enabled': {'type': 'boolean'},
                     'restrictions': {
                         'type': 'array',
                         'items': {'type': ['string', 'object']}}}}

    attr_root = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'attributes': {'type': 'object'}}}


class SchemaAttributesV6_1(object):
    _condition = {'type': 'string'}

    @property
    def _full_restriction(self):
        return {
            'type': 'object',
            'required': ['condition'],
            'properties': {
                'condition': self._condition,
                'message': {'type': 'string'},
                'action': {'type': 'string'}}}

    _short_restriction = {
        'type': 'object',
        'minProperties': 1,
        'maxProperties': 1}

    @property
    def _restrictions(self):
        return {
            'type': 'array',
            'minItems': 1,
            'items': {
                'anyOf': [
                    self._condition,
                    self._full_restriction,
                    self._short_restriction]}}

    @property
    def attr_element(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['type', 'label', 'weight', 'value'],
            'properties': {
                'type': {'type': 'string'},
                'weight': {'type': 'integer'},
                'value': {'type': ['string', 'boolean']},
                'label': {'type': 'string'},
                'restrictions': self._restrictions,
                'values': {'type': 'array', 'items':
                    {'type': 'object',
                     'required': ['data', 'label'],
                     'properties': {
                         'data': {'type': 'string'},
                         'label': {'type': 'string'}}}}}
        }

    @property
    def attr_meta(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'weight': {'type': 'integer'},
                'toggleable': {'type': 'boolean'},
                'enabled': {'type': 'boolean'},
                'restrictions': self._restrictions}
        }

    attr_root = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'attributes': {'type': 'object'}}}


class SchemaAttributesV8_0(object):
    @property
    def condition(self):
        return {'type': 'string'}

    @property
    def full_restriction(self):
        return {
            'type': 'object',
            'required': ['condition'],
            'properties': {
                'condition': self.condition,
                'message': {'type': 'string'},
                'action': {'type': 'string'}
            }
        }

    @property
    def short_restriction(self):
        return {
            'type': 'object',
            'minProperties': 1,
            'maxProperties': 1}

    @property
    def restrictions(self):
        return {
            'type': 'array',
            'minItems': 1,
            'items': {
                'anyOf': [
                    self.condition,
                    self.full_restriction,
                    self.short_restriction
                ]
            }
        }

    @property
    def attr_element(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': ['type', 'label', 'weight', 'value'],
            'properties': {
                'type': {'type': 'string'},
                'weight': {'type': 'integer'},
                'value': {'anyOf': [
                    {'type': 'string'},
                    {'type': 'boolean'},
                    {
                        'type': 'object',
                        'properties': {'generator': {'type': 'string'}}
                    }
                ]},
                'label': {'type': 'string'},
                'restrictions': self.restrictions,
                'values': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['data', 'label'],
                        'properties': {
                            'data': {'type': 'string'},
                            'label': {'type': 'string'}
                        }
                    }
                }
            }
        }

    @property
    def attr_meta(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'weight': {'type': 'integer'},
                'toggleable': {'type': 'boolean'},
                'enabled': {'type': 'boolean'},
                'restrictions': self.restrictions
            }
        }

    @property
    def attr_root(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'required': [],
            'properties': {
                'attributes': {
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
        }


env_config_v6_0 = EnvConfigSchemaV6_0()
attr_elements_v6_0 = AttrElementsSchemaV6_0()
attributes_v6_1 = SchemaAttributesV6_1()
attributes_v8_0 = SchemaAttributesV8_0()
