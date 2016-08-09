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

from fuel_plugin_builder.loaders.loader_v3 import PluginLoaderV3
from fuel_plugin_builder.validators.validator_v3 import ValidatorV3
from .base import FakeFSTest


class TestValidatorV3(FakeFSTest):
    __test__ = True
    validator_class = ValidatorV3
    loader_class = PluginLoaderV3
    package_version = '3.0.0'
