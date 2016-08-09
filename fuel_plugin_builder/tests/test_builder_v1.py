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

from __future__ import unicode_literals

import mock

from fuel_plugin_builder import builders
from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.test_builder_base import BaseBuildTestCase


class TestBuilderV1(BaseBuildTestCase):
    __test__ = True
    builder_class = builders.BuilderV1

    fake_metadata = {
        'releases': BaseBuildTestCase.releases,
        'version': '1.2.3',
        'name': 'plugin_name',
        'package_version': '1.0.0'
    }

    @mock.patch('fuel_plugin_builder.utils.make_tar_gz')
    def test_make_package(self, make_tar_gz_m):
        self.builder.make_package()
        tar_path = '/tmp/fuel_plugin/plugin_name-1.2.3.fp'

        make_tar_gz_m.assert_called_once_with(
            self.builder.build_src_dir,
            tar_path,
            'plugin_name-1.2.3')

    @mock.patch('fuel_plugin_builder.utils.which',
                return_value=False)
    def test_check_requirements_raises_error(self, _):
        self.assertRaisesRegexp(
            errors.FuelCannotFindCommandError,
            'Cannot find commands "rpm, createrepo, dpkg-scanpackages", '
            'install required commands and try again',
            self.builder._check_requirements)
