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

from fuel_plugin_builder import loaders
from fuel_plugin_builder.tests.base import FakeFSTest
from fuel_plugin_builder import validators

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
                    "public_ip_required": False,
                    "description": "Write description for your role",
                    "weight": 1000,
                    "name": "Set here the name for the role. This name will "
                            "be displayed in the Fuel web UI"
                }
            },
            "network_roles": [
                {
                    "id": "example_net_role",
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
                    "default_mapping": "public"
                }
            ],
            "name": "ExampleRelease",
            "bond_attributes": None,
            "repository_path": "repositories/ubuntu",
            "vmware_attributes": None,
            "graphs": [
                {
                    "graph": {
                        "tasks": [
                            {
                                "parameters": {
                                    "retries": 10,
                                    "puppet_modules": ".",
                                    "puppet_manifest": "provision.pp",
                                    "timeout": 3600
                                },
                                "version": "2.0.0",
                                "type": "puppet",
                                "id": "provision",
                                "roles": "*"
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
                                "role": [
                                    "test-plugin_role"
                                ],
                                "type": "group",
                                "id": "test-plugin_role",
                                "parameters": {
                                    "strategy": {
                                        "type": "parallel"
                                    }
                                }
                            },
                            {
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
                                "version": "2.0.0",
                                "role": [
                                    "test-plugin_role"
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
                                "parameters": {
                                    "retries": 10,
                                    "puppet_modules": ".",
                                    "puppet_manifest": "delete.pp",
                                    "timeout": 3600
                                },
                                "version": "2.1.0",
                                "type": "puppet",
                                "id": "delete",
                                "roles": [
                                    "deleted"
                                ]
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
                                "version": "2.1.0",
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
                                "role": [
                                    "test-plugin_role"
                                ],
                                "type": "group",
                                "id": "test-plugin_role",
                                "parameters": {
                                    "strategy": {
                                        "type": "parallel"
                                    }
                                }
                            },
                            {
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
                                "version": "2.0.0",
                                "role": [
                                    "test-plugin_role"
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
            "version": "1.0.0",
            "deployment_scripts_path": "deployment_scripts/",
            "components": [
                {
                    "description": "Component description (optional)",
                    "incompatible": [],
                    "label": "Plugin label, that will be shown on UI",
                    "compatible": [],
                    "requires": [],
                    "name": "additional_service:test-plugin"
                }
            ],
            "attributes": None,
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
            "networks": None,
            "deployment_tasks": [
                {
                    "role": [
                        "test-plugin_role"
                    ],
                    "type": "group",
                    "id": "test-plugin_role",
                    "parameters": {
                        "strategy": {
                            "type": "parallel"
                        }
                    }
                },
                {
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
                    "version": "2.0.0",
                    "role": [
                        "test-plugin_role"
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
            "node_attributes": None
        }
    ],
    "title": "Title for test-plugin plugin",
    "package_version": "5.0.0",
    "volumes_metadata": {
        "volumes_roles_mapping": {
            "test-plugin": [
                {
                    "id": "os",
                    "allocate_size": "min"
                }
            ]
        },
        "volumes": []
    },
    "attributes_metadata": {
        "attributes": {
            "test-plugin_text": {
                "weight": 25,
                "type": "text",
                "description": "Description for text field",
                "value": "Set default value",
                "label": "Text field"
            }
        }
    },
    "is_hotpluggable": False,
    "version": "1.0.0",
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
    "roles_metadata": {
        "test-plugin": {
            "has_primary": False,
            "public_ip_required": False,
            "description": "Write description for your role",
            "weight": 1000,
            "name": "Set here the name for the role. This name will be "
                    "displayed in the Fuel web UI"
        }
    },
    "homepage": "https://github.com/openstack/fuel-plugins",
    "network_roles_metadata": [
        {
            "id": "example_net_role",
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
            "default_mapping": "public"
        }
    ],
    "deployment_tasks": [
        {
            "role": [
                "test-plugin"
            ],
            "type": "group",
            "id": "test-plugin",
            "parameters": {
                "strategy": {
                    "type": "parallel"
                }
            }
        },
        {
            "parameters": {
                "puppet_modules": ".",
                "puppet_manifest": "deploy.pp",
                "timeout": 3600
            },
            "requires": [
                "deploy_start"
            ],
            "groups": [
                "test-plugin"
            ],
            "required_for": [
                "deploy_end"
            ],
            "type": "puppet",
            "id": "test-plugin-deployment-puppet"
        }
    ],
    "name": "test-plugin"
}


class TestLoaderV5(FakeFSTest):
    validator_class = validators.ValidatorV5
    loader_class = loaders.PluginLoaderV5
    package_version = '5.0.0'

    def test_loaded_ok(self):
        self.assertIn(u'Success!', self.data_tree.report.render())
        self.assertFalse(self.data_tree.report.is_failed())
        self.assertEqual(PLUGIN_V5_DATA, self.data_tree)

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
                r'repositories\/ubuntu is invalid directory',
                data.report.render()))
        self.assertTrue(
            re.search(
                r'deployment_scripts\/ is invalid directory',
                data.report.render()))
