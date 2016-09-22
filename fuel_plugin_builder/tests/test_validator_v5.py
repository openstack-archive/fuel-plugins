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
from fuel_plugin_builder import validators
from fuel_plugin_builder.tests.base import FakeFSTest


class TestValidatorV5(FakeFSTest):
    validator_class = validators.ValidatorV5
    loader_class = loaders.PluginLoaderV5
    package_version = '5.0.0'

    __test__ = True

    def test_validate(self):
        report = self.validator.validate(self.data_tree)
        self.assertIn(u'Success!', report.render())

    def test_fuel_version_legacy_warning(self):
        self.data_tree.update(
            self._make_fake_metadata_data(fuel_version=['9.1'])
        )
        report = self.validator.validate(self.data_tree)
        self.assertIn(u'WARNING: "fuel_version" field in metadata.yaml is '
                      u'deprecated and will be removed in further Fuel '
                      u'releases.', report.render())
        self.assertFalse(report.is_failed())

    def test_check_tasks_schema_validation_failed(self):
        bad_tasks_data = [
            {
                'type': 'shell',
                'parameters': {
                    'timeout': 3
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'parameters': {
                    'timeout': 3,
                    'cmd': 'xx'
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'shell',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': 'xx',
                    'puppet_modules': 'yy',
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': 'xx',
                    'puppet_modules': 'yy',
                    'retries': 'asd',
                },
                'stage': 'post_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': 'xx',
                    'puppet_modules': '',
                    'retries': 1,
                },
                'stage': 'pre_deployment',
                'role': '*'
            },
            {
                'type': 'puppet',
                'parameters': {
                    'timeout': 3,
                    'puppet_manifest': '',
                    'puppet_modules': 'yy',
                    'retries': 1,
                },
                'stage': 'pre_deployment',
                'role': '*'
            }
        ]
        self.data_tree['releases'][0]['graphs'][0]['tasks'] = \
            bad_tasks_data
        report = self.validator.validate(self.data_tree)
        self.assertEqual(report.count_failures(), 7 + 1)
        self.assertIn('Failure!', report.render())

    def test_check_tasks_schema_validation_passed(self):
        data_sets = [
            [
                {
                    'id': 'test1',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
            ],
            [
                {
                    'id': 'test1',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test2',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
            ],
            [
                {
                    'id': 'test3',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test4',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'xx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test5',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                }
            ],
            [
                {
                    'id': 'test1',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test2',
                    'type': 'shell',
                    'parameters': {
                        'timeout': 3,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'yy',
                        'cmd': 'reboot'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test3',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'retries': 10,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': '*'
                },
                {
                    'id': 'test4',
                    'type': 'puppet',
                    'parameters': {
                        'timeout': 3,
                        'retries': 10,
                        'puppet_manifest': 'xx',
                        'puppet_modules': 'xxx'
                    },
                    'stage': 'post_deployment',
                    'role': 'master'
                },
            ]
        ]
        for data in data_sets:
            self.data_tree['releases'][0]['graphs'][0]['tasks'] = data
            report = self.validator.validate(self.data_tree)
            self.assertFalse(report.is_failed())
            self.assertIn('Success!', report.render())

    def test_check_node_attributes_schema_validation_failed(self):
        data_sets = [
            {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    '123': {
                        'label': 'Attribute without type',
                        'description': 'Attribute without type',
                        'value': ''
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute_without_label': {
                        'description': 'Attribute without label',
                        'type': 'text',
                        'value': 'attribute_value'
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute_without_value': {
                        'label': 'Attribute without value',
                        'description': 'Attribute without value',
                        'type': 'text',
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute-1': {
                        'description': 'Attribute with wrong label type',
                        'label': 123,
                        'type': 'checkbox',
                        'value': ''
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute-2': {
                        'label': 'Attribute with wrong type type',
                        'type': [],
                        'value': ''
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute-3': {
                        'label': 'Attribute with wrong description type',
                        'type': 'text',
                        'value': '',
                        'description': False
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute-4': {
                        'label': 'Attribute with wrong restrictions type',
                        'type': 'text',
                        'value': '',
                        'restrictions': {}
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'group': 'Metadata without label'
                    },
                    'attribute_a': {
                        'label': 'Some label',
                        'type': 'text',
                        'value': '',
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': None,
                        'group': 'Metadata with wrong label type'
                    },
                    'attribute_a': {
                        'label': 'Some label',
                        'type': 'text',
                        'value': '',
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': None,
                        'group': 'Metadata with wrong restriction type',
                        'restrictions': 'restrictions'
                    },
                    'attribute_a': {
                        'label': 'Some label',
                        'type': 'text',
                        'value': '',
                    }
                }
            }, {
                'metadata': {
                    'label': 'Some label'
                },
                'attribute': {
                    'label': 'Missed plugin section. Wrong level nesting.',
                    'type': 'text',
                    'value': ''
                }
            }, {
                'extra_level': {
                    'plugin_section': {
                        'metadata': {
                            'label': 'Some label'
                        },
                        'attribute-4': {
                            'label': 'Attribute with extra nesting level',
                            'type': 'text',
                            'value': ''
                        }
                    }
                }
            }, {
                'plugin_section': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'uns@pported_letters=!n_attr_name*': {
                        'label': 'Attribute with wrong name',
                        'type': 'text',
                        'value': ''
                    }
                }
            }, {
                'uns@pported_letters=!n_section_name': {
                    'metadata': {
                        'label': 'Some label'
                    },
                    'attribute': {
                        'label': 'Attribute with wrong name',
                        'type': 'text',
                        'value': ''
                    }
                }
            },
            ['wrong interface attributes object type']
        ]

        for data in data_sets:
            self.data_tree['node_attributes_metadata'] = data
            report = self.validator.validate(self.data_tree)
            self.assertIn('Failure!', report.render())
            self.assertTrue(report.is_failed())

    def test_check_node_attributes_schema_validation_passed(self):
        data = {
            'plugin_section': {
                'metadata': {
                    'label': 'Some label'
                },
                '123': {
                    'label': 'Attribute with min required fields',
                    'type': 'text',
                    'value': ''
                }
            },
            'plugin_section123': {
                'Attribute_1': {
                    'label': 'Attribute with restrictions & complex value',
                    'description': 'Some attribute description',
                    'type': 'text',
                    'value': {'key1': ['val_1', 'val_2']},
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        }
                    ]
                },
                'attribute-2': {
                    'label': 'Attribute with additional fields',
                    'type': 'number',
                    'description': 'Some attribute description',
                    'value': 10,
                    'min': 0
                },
                'metadata': {
                    'label': 'Metadata with extra field & restrictions',
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        }
                    ],
                    'group': 'group A'
                }
            }
        }

        self.data_tree['node_attributes_metadata'] = data
        report = self.validator.validate(self.data_tree)
        self.assertIn('Success!', report.render())
        self.assertFalse(report.is_failed())

    def test_check_interface_attributes_schema_validation_failed(self):
        data_sets = [
            {
                '123': {
                    'label': 'Attribute without type',
                    'description': 'Attribute without type',
                    'value': ''
                }
            },
            {
                'attribute_without_label': {
                    'description': 'Attribute without label',
                    'type': 'text',
                    'value': 'attribute_value'
                }
            }, {
                'attribute_without_value': {
                    'label': 'Attribute without value',
                    'description': 'Attribute without value',
                    'type': 'text',
                }
            },
            {
                'attribute-1': {
                    'description': 'Attribute with wrong label type',
                    'label': 123,
                    'type': 'checkbox',
                }
            },
            {
                'attribute-2': {
                    'label': 'Attribute with wrong type type',
                    'type': [],
                }
            },
            {
                'attribute-3': {
                    'label': 'Attribute with wrong description type',
                    'type': 'text',
                    'description': False
                }
            },
            {
                'attribute-4': {
                    'label': 'Attribute with wrong restrictions type',
                    'type': 'text',
                    'restrictions': {}
                }
            },
            {
                'label': 'Missed attribute name. Wrong level nesting.',
                'type': 'text',
                'value': ''
            },
            {
                'extra_level': {
                    'attribute_name': {
                        'label': 'Attribute with extra nesting level',
                        'type': 'text',
                        'value': ''
                    }
                }
            },
            {
                'uns@pported_letters=!n_attr_name*': {
                    'label': 'Attribute with wrong name',
                    'type': 'text',
                    'value': ''
                }
            },
            ['wrong interface attributes object type']
        ]

        for data in data_sets:
            self.data_tree['bond_attributes_metadata'] = data
            report = self.validator.validate(self.data_tree)
            self.assertIn('Failure!', report.render())
            self.assertTrue(report.is_failed())

    def test_check_interface_attributes_schema_validation_passed(self):
        data_sets = [
            {
                '123': {
                    'label': 'Attribute with min required fields',
                    'type': 'text',
                    'value': ''
                }
            },
            {
                'Attribute_1': {
                    'label': 'Attribute with restrictions & complex value',
                    'description': 'Some attribute description',
                    'type': 'text',
                    'value': {'key1': ['val_1', 'val_2']},
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        }
                    ]
                },
                'attribute-2': {
                    'label': 'Attribute with additional fields',
                    'type': 'number',
                    'description': 'Some attribute description',
                    'value': 10,
                    'min': 0
                },
                'metadata': {
                    'label': 'Some metadata'
                }
            }
        ]

        for data in data_sets:
            self.data_tree['nic_attributes_metadata'] = data
            report = self.validator.validate(self.data_tree)
            self.assertIn('Success!', report.render())
            self.assertFalse(report.is_failed())
