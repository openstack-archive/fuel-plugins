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

from loader_base import LoaderBase


class LoaderV4(LoaderBase):
    _map_paths_to_data_keys = {
        'tasks': 'tasks.yaml',
        'environment_config': 'environment_config.yaml',
        'deployment_tasks': 'deployment_tasks.yaml',
        'network_roles': 'network_roles.yaml',
        'node_roles': 'node_roles.yaml',
        'volumes': 'volumes.yaml',
        'components': 'components.yaml'
    }
