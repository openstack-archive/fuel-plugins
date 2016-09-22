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

import logging

from fuel_plugin_builder import schemas
from fuel_plugin_builder.validators.validator_base import ValidatorBase

logger = logging.getLogger(__name__)


class ValidatorV1(ValidatorBase):
    package_version = '1.0.0'
    minimal_fuel_version = '6.0'

    _data_tree_schemas = {
        '': schemas.metadata_v6_0.schema,
        'tasks': schemas.task_v0_0_2.tasks
    }
    _data_tree_multi_schemas = {
        'tasks': {
            'puppet': schemas.task_v0_0_0.puppet_task,
            'shell': schemas.task_v0_0_0.shell_task
        }
    }
    _data_tree_env_attributes = {
        'environment_config': [
            schemas.attributes_v6_1.attr_root,
            schemas.attributes_v6_1.attr_element,
            schemas.attributes_v6_1.attr_meta
        ]
    }
