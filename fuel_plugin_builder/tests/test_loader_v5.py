import re

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

import os

from fuel_plugin_builder import loaders
from fuel_plugin_builder import validators
from tests.test_loader_base import BaseLoaderTestCase

PLUGIN_V5_DATA = {
    "description": "Please describe your plugin here",
    "releases": [
        {
            "is_release": True,
            "operating_system": "ubuntu",
            "nic_attributes": None,
            "description": "Example Release Description",
            "roles": {
                "test-plugin_role": {
                    "has_primary": False,
                    "description": "Write description for your role",
                    "name": "Set here the name for the role. This name will "
                            "be displayed in the Fuel web UI",
                    "weight": 1000,
                    "public_ip_required": False
                }
            },
            "graphs": [
                {
                    "graph": {
                        "tasks": [
                            {
                                "roles": "*",
                                "version": "2.0.0",
                                "type": "puppet",
                                "id": "provision",
                                "parameters": {
                                    "retries": 10,
                                    "puppet_modules": ".",
                                    "puppet_manifest": "provision.pp",
                                    "timeout": 3600
                                }
                            }
                        ],
                        "name": "provisioning"
                    },
                    "type": "provisioning"
                },
                {
                    "graph": {
                        "tasks": [
                            {
                                "type": "group",
                                "role": [
                                    "test-plugin_role"
                                ],
                                "id": "test-plugin_role",
                                "parameters": {
                                    "strategy": {
                                        "type": "parallel"
                                    }
                                }
                            },
                            {
                                "version": "2.0.0",
                                "role": [
                                    "test-plugin_role"
                                ],
                                "parameters": {
                                    "puppet_modules": ".",
                                    "puppet_manifest": "deploy.pp",
                                    "timeout": 3600
                                },
                                "cross-depended-by": [
                                    {
                                        "name": "deploy_end"
                                    }
                                ],
                                "cross-depends": [
                                    {
                                        "name": "deploy_start"
                                    }
                                ],
                                "type": "puppet",
                                "id": "test-plugin-deployment-puppet"
                            }
                        ],
                        "name": "default deployment graph"
                    },
                    "type": "deployment"
                },
                {
                    "graph": {
                        "tasks": [
                            {
                                "roles": [
                                    "deleted"
                                ],
                                "version": "2.1.0",
                                "type": "puppet",
                                "id": "delete",
                                "parameters": {
                                    "retries": 10,
                                    "puppet_modules": ".",
                                    "puppet_manifest": "delete.pp",
                                    "timeout": 3600
                                }
                            }
                        ],
                        "name": "deletion"
                    },
                    "type": "deletion"
                },
                {
                    "graph": {
                        "tasks": [
                            {
                                "version": "2.1.0",
                                "parameters": {
                                    "retries": 10,
                                    "puppet_modules": ".",
                                    "puppet_manifest": "delete.pp",
                                    "timeout": 3600
                                },
                                "roles": [
                                    "*",
                                    "master"
                                ],
                                "required_for": [
                                    "deploy_start"
                                ],
                                "type": "puppet",
                                "id": "verify_networks"
                            }
                        ],
                        "name": "network_veification"
                    },
                    "type": "network_verification"
                },
                {
                    "graph": {
                        "tasks": [
                            {
                                "type": "group",
                                "role": [
                                    "test-plugin_role"
                                ],
                                "id": "test-plugin_role",
                                "parameters": {
                                    "strategy": {
                                        "type": "parallel"
                                    }
                                }
                            },
                            {
                                "version": "2.0.0",
                                "role": [
                                    "test-plugin_role"
                                ],
                                "parameters": {
                                    "puppet_modules": ".",
                                    "puppet_manifest": "deploy.pp",
                                    "timeout": 3600
                                },
                                "cross-depended-by": [
                                    {
                                        "name": "deploy_end"
                                    }
                                ],
                                "cross-depends": [
                                    {
                                        "name": "deploy_start"
                                    }
                                ],
                                "type": "puppet",
                                "id": "test-plugin-deployment-puppet"
                            }
                        ],
                        "name": "deployment-graph-name"
                    },
                    "type": "default"
                }
            ],
            "components": [
                {
                    "compatible": [],
                    "description": "Component description (optional)",
                    "name": "additional_service:test-plugin",
                    "incompatible": [],
                    "requires": [],
                    "label": "Plugin label, that will be shown on UI"
                }
            ],
            "bond_attributes": None,
            "network_roles": [
                {
                    "default_mapping": "public",
                    "properties": {
                        "subnet": True,
                        "vip": [
                            {
                                "namespace": "haproxy",
                                "name": "vip_name"
                            }
                        ],
                        "gateway": False
                    },
                    "id": "example_net_role"
                }
            ],
            "networks": None,
            "repository_path": "repositories/ubuntu",
            "version": "0.0.1",
            "deployment_scripts_path": "deployment_scripts/",
            "volumes": {
                "volumes_roles_mapping": {
                    "test-plugin_role": [
                        {
                            "id": "os",
                            "allocate_size": "min"
                        }
                    ]
                },
                "volumes": []
            },
            "attributes": None,
            "node_attributes": None,
            "vmware_attributes": None,
            "deployment_tasks": "graphs/deployment_tasks.yaml",
            "name": "ExampleRelease"
        }
    ],
    "title": "Title for test-plugin plugin",
    "package_version": "5.0.0",
    "is_hotpluggable": False,
    "version": "0.0.1",
    "fuel_version": [
        "9.1"
    ],
    "groups": [],
    "authors": [
        "Specify author or company name"
    ],
    "licenses": [
        "Apache License Version 2.0"
    ],
    "homepage": "https://github.com/openstack/fuel-plugins",
    "name": "test-plugin"
}


class TestLoaderV5(BaseLoaderTestCase):
    # will be loaded to fake fs
    plugin_path = os.path.abspath('./templates/v5/plugin_data')
    validator = validators.ValidatorV5()
    loader = loaders.PluginLoaderV5(plugin_path)
    maxDiff = None

    def test_loaded_ok(self):
        self.assertIn(u'Success!', self.data.report.render())
        self.assertFalse(self.data.report.is_failed())
        self.assertEqual(PLUGIN_V5_DATA, self.data)

    def test_loader_fail_on_missing_graph_file(self):
        self.fs.RemoveObject(
            self._make_fakefs_path('graphs')
        )
        data = self.loader.load(self.plugin_path)
        self.assertIn(u"graphs/deployment_tasks.yaml", data.report.render())
        self.assertIn(u"Can't find file.", data.report.render())
        self.assertTrue(data.report.is_failed())
        self.assertEqual(
            None,
            data['releases'][0]['graphs'][0].get('graph')
        )
        self.assertEqual(
            'graphs/provisioning.yaml',
            data['releases'][0]['graphs'][0].get('graph_path')
        )
        self.assertEqual(
            'graphs/deployment_tasks.yaml',
            data['releases'][0]['graphs'][1]['graph'].get('tasks_path')
        )

    def test_loader_fail_on_missing_attributes_file(self):
        self.fs.RemoveObject(
            self._make_fakefs_path('attributes/attributes.yaml')
        )
        data = self.loader.load(self.plugin_path)
        self.assertIn(u"attributes/attributes.yaml", data.report.render())
        self.assertIn(u"Can't find file.", data.report.render())
        self.assertTrue(data.report.is_failed())
        self.assertEqual(
            None,
            data['releases'][0].get('attributes')
        )
        self.assertEqual(
            'attributes/attributes.yaml',
            data['releases'][0].get('attributes_path')
        )

    def test_fail_on_bad_release_path(self):
        self.fs.RemoveObject(
            self._make_fakefs_path('repositories/ubuntu')
        )
        self.fs.RemoveObject(
            self._make_fakefs_path('deployment_scripts/')
        )
        data = self.loader.load(self.plugin_path)
        self.assertTrue(data.report.is_failed())
        self.assertTrue(
            re.search(
                'repositories/ubuntu is invalid directory',
                data.report.render()))
        self.assertTrue(
            re.search(
                'repositories/ubuntu is invalid directory',
                data.report.render()))
