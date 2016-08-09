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

import os
from StringIO import StringIO

import mock
import yaml
from pyfakefs import fake_filesystem_unittest

from fuel_plugin_builder import consts
from fuel_plugin_builder import loaders
from fuel_plugin_builder import utils
from fuel_plugin_builder import validators
from fuel_plugin_builder import version_mapping


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

    def _make_fake_metadata_data(self, **kwargs):
        """Generate metadata based on example and custom fields from kwargs.

        :return: metadata
        :rtype: dict
        """
        metadata = {
            'package_version': '5.0.0',
            'fuel_version': ['9.1']
        }
        metadata.update(kwargs)
        return metadata


class FakeFSTest(BaseTestCase, fake_filesystem_unittest.TestCase):
    plugin_path = '/tmp/plugin/'  # path inside mock FS
    fpb_dir = os.path.join(os.path.dirname(__file__), '..')

    validator_class = validators.BaseValidator
    loader_class = None
    package_version = None

    def _delete_from_fakefs(self, path):
        """Remove record from mockfs if exists.

        :param path: path
        :type path: str
        """
        fakefs_path = self._make_fakefs_path(path)
        if os.path.exists(fakefs_path):
            self.fs.RemoveObject(fakefs_path)

    def _make_fakefs_path(self, relative_path):
        """Make absolute path related to the plugin example root folder.

        :param relative_path: relative path
        :type relative_path: str
        :return: absolute path
        :rtype: str
        """
        return os.path.abspath(
            os.path.join(
                self.plugin_path, relative_path
            )
        )

    def _patch_fakefs_file(self, path, add_data):
        fakefs_path = self._make_fakefs_path(path)
        if os.path.exists(fakefs_path):
            raw_data = self.fs.GetObject(fakefs_path)
            data = yaml.safe_load(raw_data.contents)
            data.update(add_data)
        else:
            data = add_data
        self._create_fakefs_yaml(path, data)

    def _create_fakefs_yaml(self, path, new_data):
        """Replace file with new one inside mockfs

        :param path: relative path
        :type path: str|basestring
        :param new_data: list/dict structure that will be serialised to YAML
        :type new_data: dict|list
        """
        self._delete_from_fakefs(path)
        self.fs.CreateFile(
            file_path=self._make_fakefs_path(path),
            contents=yaml.dump(new_data)
        )

    def setUp(self):
        super(FakeFSTest, self).setUp()
        template_paths = version_mapping.get_plugin_for_version(
            self.package_version)['templates']

        for template_path in template_paths:
            template_path = os.path.join(self.fpb_dir, template_path)
            print("Setting up fakeFs from template {}".format(template_path))

            for root, _, file_names in os.walk(template_path):
                for filename in file_names:
                    src_path = os.path.abspath(
                        os.path.join(root, filename)
                    )
                    extension = utils.get_path_extension(src_path)
                    if extension == consts.TEMPLATE_EXTENSION:
                        content = utils.template.render_template_file(
                            src_path, plugin_name="test-plugin")
                        dst_path = os.path.join(
                            self.plugin_path,
                            os.path.relpath(
                                utils.fs.get_path_without_extension(src_path),
                                template_path
                            )
                        )
                    else:
                        dst_path = os.path.join(
                            self.plugin_path,
                            os.path.relpath(
                                src_path,
                                template_path
                            )
                        )
                        with open(src_path) as f:
                            content = f.read()
                    self.fs.CreateFile(
                        file_path=dst_path,
                        contents=content
                    )
        self.validator = self.validator_class()
        if isinstance(self.loader_class.load, mock.Mock):
            self.loader_class.load.reset_mock()
        self.setUpPyfakefs()  # setup place is important
        self.loader = self.loader_class(self.plugin_path)
        self.data_tree = self.loader.load()

    def tearDown(self):
        super(FakeFSTest, self).tearDown()