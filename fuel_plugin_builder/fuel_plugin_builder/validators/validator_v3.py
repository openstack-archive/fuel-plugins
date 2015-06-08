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

from fuel_plugin_builder.validators.schemas import v3
from fuel_plugin_builder.validators import validator_v2


class ValidatorV3(validator_v2.ValidatorV2):

    schema = v3.SchemaV3()

    @property
    def basic_version(self):
        return '7.0'

    def __init__(self, *args, **kwargs):
        super(ValidatorV3, self).__init__(*args, **kwargs)
