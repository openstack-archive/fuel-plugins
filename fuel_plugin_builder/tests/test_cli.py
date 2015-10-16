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

import mock

from fuel_plugin_builder.cli import package_version_check
from fuel_plugin_builder.cli import perform_action
from fuel_plugin_builder.tests.base import BaseTestCase


class TestCli(BaseTestCase):

    @mock.patch('fuel_plugin_builder.cli.actions')
    def test_perform_action_create_with_package_version(self, actions_mock):
        args = mock.MagicMock(create='plugin_path', package_version='2.0.0')
        creatre_obj = mock.MagicMock()
        actions_mock.CreatePlugin.return_value = creatre_obj

        perform_action(args)

        actions_mock.CreatePlugin.assert_called_once_with(
            'plugin_path',
            '2.0.0')
        creatre_obj.run.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.cli.actions')
    def test_perform_action_create_without_package_version(self, actions_mock):
        args = mock.MagicMock(create='plugin_path', package_version=None)
        creatre_obj = mock.MagicMock()
        actions_mock.CreatePlugin.return_value = creatre_obj

        perform_action(args)

        actions_mock.CreatePlugin.assert_called_once_with('plugin_path', None)
        creatre_obj.run.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.cli.actions.make_builder')
    def test_perform_action_build(self, builder_mock):
        args = mock.MagicMock(
            create=None,
            build='plugin_path')
        build_obj = mock.MagicMock()
        builder_mock.return_value = build_obj

        perform_action(args)

        builder_mock.assert_called_once_with('plugin_path')
        build_obj.run.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.cli.ValidatorManager')
    def test_perform_check(self, validator_mock):
        args = mock.MagicMock(
            create=None,
            build=None,
            check='plugin_path')
        build_obj = mock.MagicMock()
        validator_mock.BuildPlugin.return_value = build_obj

        perform_action(args)

        validator_mock.assert_called_once_with('plugin_path')

    def test_package_version_check_with_create_and_version(self):
        args = mock.MagicMock(
            create='plugin_path',
            package_version='2.0.0',
            build=None,
            check=None)

        parser = mock.MagicMock()

        package_version_check(args, parser)
        self.method_was_not_called(parser.error)

    def test_package_version_check_with_create_and_without_version(self):
        args = mock.MagicMock(
            create='plugin_path',
            package_version=None,
            build=None,
            check=None)

        parser = mock.MagicMock()

        package_version_check(args, parser)
        self.method_was_not_called(parser.error)

    def test_package_version_check_with_build_and_version(self):
        args = mock.MagicMock(
            create=None,
            package_version='2.0.0',
            build='plugin_path',
            check=None)

        parser = mock.MagicMock()

        package_version_check(args, parser)
        parser.error.assert_called_with(
            '--package-version works only with --create')

    def test_package_version_check_with_build_and_without_version(self):
        args = mock.MagicMock(
            create=None,
            package_version=None,
            build='plugin_path',
            check=None)

        parser = mock.MagicMock()

        package_version_check(args, parser)
        self.method_was_not_called(parser.error)

    def test_package_version_check_with_check_and_version(self):
        args = mock.MagicMock(
            create=None,
            package_version='2.0.0',
            build=None,
            check='plugin_path')

        parser = mock.MagicMock()

        package_version_check(args, parser)

        parser.error.assert_called_with(
            '--package-version works only with --create')

    def test_package_version_check_with_check_and_without_version(self):
        args = mock.MagicMock(
            create=None,
            package_version=None,
            build=None,
            check='plugin_path')

        parser = mock.MagicMock()

        package_version_check(args, parser)
        self.method_was_not_called(parser.error)
