# -*- coding: utf-8 -*-
#
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
from fuel_plugin_builder import schemas
from fuel_plugin_builder.validators import ValidatorV2


class ValidatorV3(ValidatorV2):
    package_version = '3.0.0'
    minimal_fuel_version = '7.0'

    _data_tree_schemas = {
        '': schemas.metadata_v7_0.schema,
        'tasks': schemas.task_v0_0_2.tasks,
        'deployment_tasks': schemas.task_v1_0_0.tasks,
        'network_roles_metadata': schemas.network_roles_v7_0.schema,
        'node_roles_metadata': schemas.node_roles_v7_0.schema,
        'volumes_metadata': schemas.volumes_v7_0.schema
    }
    _data_tree_multi_schemas = {
        'tasks': {
            'puppet': schemas.task_v0_0_0.puppet_task,
            'shell': schemas.task_v0_0_0.shell_task,
            'reboot': schemas.task_v1_0_0.reboot_task
        },
        'deployment_tasks': {
            'puppet': schemas.task_v1_0_0.puppet_task,
            'shell': schemas.task_v1_0_0.shell_task,
            'group': schemas.task_v1_0_0.group_task,
            'skipped': schemas.task_v1_0_0.skipped_task,
            'copy_files': schemas.task_v1_0_0.copy_files_task,
            'sync': schemas.task_v1_0_0.sync_task,
            'upload_file': schemas.task_v1_0_0.upload_file_task,
            'stage': schemas.task_v1_0_0.stage_task,
            'reboot': schemas.task_v1_0_0.reboot_task
        }
    }
