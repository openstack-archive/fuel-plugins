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

from fuel_plugin_builder.validators import schemas

from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder.validators.base import Inspection

from fuel_plugin_builder.validators.checks import EnvConfigAttrsIsValid
from fuel_plugin_builder.validators.checks import IsCompatible
from fuel_plugin_builder.validators.checks import IsFile
from fuel_plugin_builder.validators.checks import JsonSchemaIsValid
from fuel_plugin_builder.validators.checks import MultiJsonSchemaIsValid
from fuel_plugin_builder.validators.checks import ReleasesPathsIsValid


class ValidatorV4(BaseValidator):
    schema_v4 = schemas.SchemaV4()
    schema_v3 = schemas.SchemaV3()

    @property
    def inspections(self):
        return [
            Inspection(
                name='meta',
                path=self._get_plugin_path('metadata.yaml'),
                checks=[
                    IsFile(),
                    IsCompatible('8.0'),
                    JsonSchemaIsValid(self.schema_v4.metadata_schema),
                    ReleasesPathsIsValid(base_path=self._get_plugin_path())
                ]
            ),
            Inspection(
                name='env_conf',
                path=self._get_plugin_path('environment_config.yaml'),
                checks=[
                    IsFile(),
                    JsonSchemaIsValid(self.schema_v4.attr_root_schema),
                    EnvConfigAttrsIsValid(
                        self.schema_v4.attr_root_schema,
                        self.schema_v4.attr_element_schema,
                        self.schema_v4.attr_meta_schema
                    )
                ]
            ),
            Inspection(
                name='tasks',
                path=self._get_plugin_path('deployment_tasks.yaml'),
                checks=[
                    IsFile(),
                    JsonSchemaIsValid(self.schema_v4.deployment_task_schema),
                    MultiJsonSchemaIsValid({
                        'puppet': self.schema_v4.puppet_task,
                        'shell': self.schema_v4.shell_task,
                        'group': self.schema_v4.group_task,
                        'skipped': self.schema_v4.skipped_task,
                        'copy_files': self.schema_v4.copy_files_task,
                        'sync': self.schema_v4.sync_task,
                        'upload_file': self.schema_v4.upload_file_task,
                        'stage': self.schema_v4.stage_task,
                        'reboot': self.schema_v4.reboot_task
                    })
                ]
            ),
            Inspection(
                name='network_roles',
                path=self._get_plugin_path('network_roles.yaml'),
                checks=[
                    IsFile(required=False),
                    JsonSchemaIsValid(self.schema_v4.network_roles_schema)
                ]
            ),
            Inspection(
                name='volumes',
                path=self._get_plugin_path('volumes.yaml'),
                checks=[
                    IsFile(required=False),
                    JsonSchemaIsValid(self.schema_v4.volume_schema)
                ]
            ),
            Inspection(
                name='legacy_tasks',
                path=self._get_plugin_path('tasks.yaml'),
                checks=[
                    IsFile(required=False),
                    JsonSchemaIsValid(self.schema_v3.tasks_schema)
                ]
            ),
            Inspection(
                name='components',
                path=self._get_plugin_path('components.yaml'),
                checks=[
                    IsFile(required=False),
                    JsonSchemaIsValid(self.schema_v4.components_schema)
                ]
            )
        ]
