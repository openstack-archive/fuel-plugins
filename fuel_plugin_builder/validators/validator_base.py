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

import logging

import six

from fuel_plugin_builder import checks
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class ValidatorBase(object):
    """Base Validator.

    New ValidatorBase targeted to plugin package version >= 5.0.0 and using
    Checks to describe custom logic and providing output based on
    utils.ReportNode class.

    Check is a basic logic unit that performing validations with given
    parameters.
    """

    package_version = '0.0.1'
    minimal_fuel_version = '0.1'
    _metadata_schema = None
    _data_tree_schemas = {}
    _data_tree_multi_schemas = {}
    _data_tree_env_attributes = {}
    _validator = None

    def validate(self, data_tree):
        """Validate data tree and return report.

        :param data_tree: plugin data tree starting from the metadata.yaml dict
        :type data_tree: dict

        :return: report
        :rtype: utils.ReportNode
        """
        report = utils.ReportNode('Validating data')
        # fixme(ikutukov): compatibility check should be moved out from base
        # after the plugin package > 5.0.0 will be defined
        report.add_nodes(
            checks.fuel_ver_compatible_with_package_ver(
                self.minimal_fuel_version, data_tree
            )
        )
        report.add_nodes(
            self.check_data_tree_branches_schema(data_tree)
        )
        report.add_nodes(
            self.check_data_tree_multi_branches_schema(data_tree)
        )
        report.add_nodes(
            self.check_data_tree_env_attributes(data_tree)
        )
        return report

    def check_data_tree_branches_schema(self, data_tree):
        schema_check_report = utils.ReportNode('Checking schemas')
        for branch_key, schema in \
                six.iteritems(self._data_tree_schemas):
            if branch_key:
                if data_tree.get(branch_key):
                    report = utils.ReportNode(branch_key)
                    report.add_nodes(
                        checks.json_schema_is_valid(
                            schema,
                            data_tree[branch_key],
                            validator=self._validator
                        )
                    )
                    schema_check_report.add_nodes(report)
            else:
                report = utils.ReportNode('metadata')
                report.add_nodes(
                    checks.json_schema_is_valid(schema, data_tree,
                                                validator=self._validator)
                )
                schema_check_report.add_nodes(report)

        return schema_check_report

    def check_data_tree_multi_branches_schema(self, data_tree):
        schema_check_report = utils.ReportNode('Checking multi schemas')
        for branch_key, multi_schema in \
                six.iteritems(self._data_tree_multi_schemas):
            if data_tree.get(branch_key):
                report = utils.ReportNode(branch_key)
                report.add_nodes(
                    checks.multi_json_schema_is_valid(
                        multi_schema,
                        data_tree[branch_key],
                        validator=self._validator
                    )
                )
                schema_check_report.add_nodes(report)

        return schema_check_report

    def check_data_tree_env_attributes(self, data_tree):
        schema_check_report = utils.ReportNode(
            'Checking env attributes schemas')

        for branch_key, multi_schema in \
                six.iteritems(self._data_tree_env_attributes):
            if data_tree.get(branch_key):
                report = utils.ReportNode(branch_key)
                report.add_nodes(
                    checks.env_attributes(
                        data_tree.get(branch_key),
                        *multi_schema, validator=self._validator
                    )
                )
                schema_check_report.add_nodes(report)
        return schema_check_report
