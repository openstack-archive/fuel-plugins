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

import mock

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.test_validator_v4 import TestValidatorV4
from fuel_plugin_builder.validators.schemas import SchemaV5
from fuel_plugin_builder.validators.validator_v5 import ValidatorV5


class TestValidatorV5(TestValidatorV4):

    __test__ = True
    validator_class = ValidatorV5
    schema_class = SchemaV5
    package_version = '5.0.0'

    def setUp(self):
        super(TestValidatorV5, self).setUp()

    def test_check_schemas(self):
        mocked_methods = [
            'check_metadata_schema',
            'check_env_config_attrs',
            'check_tasks_schema',
            'check_deployment_tasks_schema',
            'check_network_roles_schema',
            'check_node_roles_schema',
            'check_volumes_schema',
            'check_components_schema',
            'check_node_attributes_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.mock_methods(
            self.validator,
            ['validate_file_by_schema', 'check_interface_attributes_schema']
        )
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(self.validator.bond_config_path),
             mock.call(self.validator.nic_config_path)],
            self.validator.check_interface_attributes_schema.call_args_list)
        for method in mocked_methods:
            getattr(self.validator, method).assert_called_once_with()

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_failed(self, utils_mock):
        fuel_version_checks = (
            (['8.0', '9.0', '10.0']),
            (['6.1', '7.0', '8.0']),
            (['6.0', '6.1', '7.0']),
            (['6.1', '7.0']),
        )

        for fuel_version in fuel_version_checks:
            mock_data = {
                'fuel_version': fuel_version,
                'package_version': '5.0.0'}
            err_msg = 'Current plugin format 5.0.0 is not compatible with ' \
                      '{0} Fuel release. Fuel version must be 9.0 or higher.' \
                      ' Please remove {0} version from metadata.yaml file or' \
                      ' downgrade package_version.'.format(fuel_version[0])

            self.check_raised_exception(
                utils_mock, mock_data,
                err_msg, self.validator.check_compatibility)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_compatibility_passed(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'fuel_version': ['9.0', '9.1', '9.2', '10.0'],
            'package_version': '5.0.0'}
        self.validator.check_compatibility()

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_interface_attributes_schema_validation_no_file(self,
                                                                  exists_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_interface_attributes_schema(mock.ANY)
        self.assertFalse(self.validator.validate_schema.called)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_interface_attributes_schema_validation_failed(self,
                                                                 utils_mock):
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
            utils_mock.parse_yaml.return_value = data
            self.assertRaises(errors.ValidationError,
                              self.validator.check_interface_attributes_schema,
                              mock.ANY)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_interface_attributes_schema_validation_passed(self,
                                                                 utils_mock):
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
            utils_mock.parse_yaml.return_value = data
            self.validator.check_interface_attributes_schema('nic_config_path')

    @mock.patch('fuel_plugin_builder.validators.base.utils.exists')
    def test_check_node_attributes_schema_validation_no_file(self,
                                                             exists_mock):
        mocked_methods = ['validate_schema']
        self.mock_methods(self.validator, mocked_methods)
        exists_mock.return_value = False
        self.validator.check_node_attributes_schema()
        self.assertFalse(self.validator.validate_schema.called)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_node_attributes_schema_validation_failed(self, utils_mock):
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
            utils_mock.parse_yaml.return_value = data
            self.assertRaises(errors.ValidationError,
                              self.validator.check_node_attributes_schema)

    @mock.patch('fuel_plugin_builder.validators.base.utils')
    def test_check_node_attributes_schema_validation_passed(self, utils_mock):
        data_sets = [
            {
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
        ]

        for data in data_sets:
            utils_mock.parse_yaml.return_value = data
            self.validator.check_node_attributes_schema()
