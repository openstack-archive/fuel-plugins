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

try:
    from unittest.case import TestCase
except ImportError:
    # Required for python 2.6
    from unittest2.case import TestCase

import mock
from StringIO import StringIO

from fuel_plugin_builder import errors


class FakeFile(StringIO):
    """It's a fake file which returns StringIO
    when file opens with 'with' statement.

    NOTE(eli): We cannot use mock_open from mock library
    here, because it hangs when we use 'with' statement,
    and when we want to read file by chunks.
    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def writelines(self, lines):
        self.write(''.join(lines))


class BaseTestCase(TestCase):
    """Base class for test cases
    """

    def method_was_not_called(self, method):
        """Checks that mocked method was not called
        """
        self.assertEqual(method.call_count, 0)

    def called_times(self, method, count):
        """Checks that mocked method was called `count` times
        """
        self.assertEqual(method.call_count, count)

    def mock_open(self, text, filename='some.yaml'):
        """Mocks builtin open function.

        Usage example:

            with mock.patch(
                '__builtin__.open',
                self.mock_open('file content')
            ):
                # call some methods that are used open() to read some
                # stuff internally
        """
        fileobj = FakeFile(text)
        setattr(fileobj, 'name', filename)
        return mock.MagicMock(return_value=fileobj)

    def mock_methods(self, obj, methods):
        """Mocks methods for object

        :param obj: object for mocking
        :param methods: list of methods for mocking
        """
        for method in methods:
            setattr(obj, method, mock.MagicMock())


@mock.patch('fuel_plugin_builder.validators.base.utils')
class BaseValidator(BaseTestCase):

    __test__ = False
    validator_class = None
    schema_class = None

    def setUp(self):
        self.plugin_path = '/tmp/plugin_path'
        self.validator = self.validator_class(self.plugin_path)

    def test_validate(self, _):
        mocked_methods = [
            'check_schemas',
            'check_tasks',
            'check_releases_paths',
            'check_compatibility',
        ]
        self.check_validate(mocked_methods)

    def test_check_schemas(self, _):
        mocked_methods = [
            'check_env_config_attrs',
            'validate_file_by_schema'
        ]
        self.mock_methods(self.validator, mocked_methods)
        self.validator.check_schemas()

        self.assertEqual(
            [mock.call(self.schema_class().metadata_schema,
                       self.validator.meta_path),
             mock.call(self.schema_class().tasks_schema,
                       self.validator.tasks_path)],
            self.validator.validate_file_by_schema.call_args_list)

        self.validator.check_env_config_attrs.assert_called_once_with()

    def test_check_releases_paths(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': '/tmp/repository_path'}]}

        utils_mock.exists.return_value = True
        self.validator.check_releases_paths()
        self.assertEqual(
            utils_mock.exists.call_args_list,
            [mock.call('/tmp/deployment_scripts_path'),
             mock.call('/tmp/repository_path')])

    def test_check_releases_paths_error(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'releases': [{
                'deployment_scripts_path': '/tmp/deployment_scripts_path',
                'repository_path': '/tmp/repository_path'}]}

        utils_mock.exists.return_value = False
        with self.assertRaisesRegexp(
                errors.ReleasesDirectoriesError,
                'Cannot find directories /tmp/deployment_scripts_path'
                ', /tmp/repository_path for release '):
            self.validator.check_releases_paths()

    def test_check_env_config_attrs_do_not_fail_if_empty(self, utils_mock):
        utils_mock.parse_yaml.return_value = None
        self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_fail_if_none(self, utils_mock):
        utils_mock.parse_yaml.return_value = {'attributes': None}
        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', None "
                "is not of type 'object', value path 'attributes'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_checks_metadata(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {'metadata': []}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', \[\] is "
                "not of type 'object', value path 'attributes -> metadata'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_checks_attrs(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {
                'key1': {
                    'type': True,
                    'label': 'text',
                    'value': 'text',
                    'weight': 1}}}

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', True is not "
                "of type 'string', value path 'attributes -> key1 -> type'"):
            self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_generator_value(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {
                'key1': {
                    'type': 'hidden',
                    'label': '',
                    'value': {'generator': 'password'},
                    'weight': 1}}}

        self.validator.check_env_config_attrs()

    def test_check_env_config_attrs_restriction_fails(self, utils_mock):
        utils_mock.parse_yaml.return_value = {
            'attributes': {
                'key1': {
                    'type': 'text',
                    'label': 'test',
                    'value': 'test',
                    'weight': 1,
                    'restrictions': [
                        {
                            'condition': 'false',
                            'action': 'disable'
                        },
                        {
                            'condition': True,
                            'action': 'hide'
                        }
                    ]
                }
            }
        }

        with self.assertRaisesRegexp(
                errors.ValidationError,
                "File '/tmp/plugin_path/environment_config.yaml', True is not "
                "of type 'string', value path "
                "'attributes -> key1 -> restrictions -> 1 -> condition"):
            self.validator.check_env_config_attrs()

    def check_raised_exception(self, utils_mock, mock_data,
                               err_msg, executed_method,
                               err_type=errors.ValidationError):
        """Check if the given error with given type was raised.

        :param obj utils_mock: fuel_plugin_builder.utils mock
        :param List[dict] mock_data: mock data
        :param str err_msg: what error message is expected
        :param function executed_method: what method should be executed
        :param Exception err_type: what error type is expected
        """
        utils_mock.parse_yaml.return_value = mock_data

        with self.assertRaisesRegexp(err_type, err_msg):
            executed_method()

    def check_validate(self, mocked_methods=[]):
        self.mock_methods(self.validator, mocked_methods)
        self.validator.validate()

        for method in mocked_methods:
            getattr(self.validator, method).assert_called_once_with()
