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

from fuel_plugin_builder.cli import perform_action
from fuel_plugin_builder.tests.base import BaseTestCase


class TestCli(BaseTestCase):

    @mock.patch('fuel_plugin_builder.cli.actions')
    def test_perform_action_create(self, actions_mock):
        args = mock.MagicMock(create='plugin_path')
        creatre_obj = mock.MagicMock()
        actions_mock.CreatePlugin.return_value = creatre_obj

        perform_action(args)

        actions_mock.CreatePlugin.assert_called_once_with('plugin_path')
        creatre_obj.run.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.cli.actions')
    def test_perform_action_build(self, actions_mock):
        args = mock.MagicMock(
            create=None,
            build='plugin_path')
        build_obj = mock.MagicMock()
        actions_mock.BuildPlugin.return_value = build_obj

        perform_action(args)

        actions_mock.BuildPlugin.assert_called_once_with('plugin_path')
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
