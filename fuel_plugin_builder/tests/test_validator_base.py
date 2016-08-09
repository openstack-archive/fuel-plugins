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

import loaders
from tests.base import FakeFSTest
import validators


class BaseValidatorTestCase(FakeFSTest):
    plugin_path = None
    validator_class = validators.BaseValidator
    loader_class = loaders.PluginLoaderBase

    def setUp(self):
        super(BaseValidatorTestCase, self).setUp()
        self.validator = self.validator_class()
        self.data_tree = self.loader_class(self.plugin_path).load()
