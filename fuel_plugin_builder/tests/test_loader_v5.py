import os
import re

import errors
import loaders
import validators

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
                    "type": "deployment"
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
    loader = loaders.LoaderV5(plugin_path)

    def test_loaded_ok(self):
        # data, report = self.loader.load(self.plugin_path)
        self.assertIn(u'Success!', self.report.render())
        self.assertFalse(self.report.is_failed())

        self.assertEqual(PLUGIN_V5_DATA, self.data_tree)

    def test_loader_fail_on_missing_graph_file(self):
        self.fs.RemoveObject(
            self._make_fakefs_path('graphs/deployment_tasks.yaml')
        )
        data, report = self.loader.load(self.plugin_path)
        self.assertIn(u"graphs/deployment_tasks.yaml", report.render())
        self.assertIn(u"Can't find file.", report.render())
        self.assertTrue(report.is_failed())
        self.assertEqual(
            None,
            data['releases'][0]['graphs'][0]['graph'].get('tasks')
        )

    def test_loader_fail_on_missing_attributes_file(self):
        self.fs.RemoveObject(
            self._make_fakefs_path('attributes/attributes.yaml')
        )
        data, report = self.loader.load(self.plugin_path)
        self.assertIn(u"attributes/attributes.yaml", report.render())
        self.assertIn(u"Can't find file.", report.render())
        self.assertTrue(report.is_failed())
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
        data, report = self.loader.load(self.plugin_path)
        self.assertTrue(report.is_failed())
        self.assertTrue(
            re.search('repositories/ubuntu *\n *ERROR', report.render()))
        self.assertTrue(
            re.search('deployment_scripts/ *\n *ERROR', report.render()))
