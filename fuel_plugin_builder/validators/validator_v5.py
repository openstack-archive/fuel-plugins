# -*- coding: utf-8 -*-
#
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
import six

from fuel_plugin_builder import consts
from fuel_plugin_builder import utils
from fuel_plugin_builder import checks
from fuel_plugin_builder import schemas
from fuel_plugin_builder.validators.base import BaseValidator
from fuel_plugin_builder import files_manager
from fuel_plugin_builder.reports import ReportNode


class ValidatorV5(BaseValidator):
    package_version = '5.0.0'
    minimal_fuel_version = '9.1'
    path_suffix = consts.PATHS_SUFFIX

    def load_data_tree(self, root_path):
        report = ReportNode(u"File structure validation: {}".format(root_path))
        data = None
        try:
            data = self._load_root_metadata_file()
        except Exception as e:
            report.error(e)

        report.info(u"Loading related files")

        def recursive_process(data):
            """ Recursively processed nested list/dict.

            :param data: data
            :type data: iterable

            :returns: data
            :rtype: list|dict
            """
            if isinstance(data, dict):
                new_data = {}
                for key in tuple(data):
                    value = data[key]
                    # we have key with path
                    if key.endswith(self.path_suffix) and isinstance(value, six.string_types):
                        if utils.fs.is_dir(self._get_absolute_path(value)):
                            report.info(u"{} is valid directory".format(
                                value))
                            # leave directories as is
                            new_data[key] = value
                        else:
                            try:
                                loaded_data = files_manager.files_manager.load(
                                    self._get_absolute_path(value)
                                )
                                cleaned_key = key[:- len(self.path_suffix)]
                                new_data[cleaned_key] = loaded_data
                            except Exception as exc:
                                path_node = ReportNode(data[key])
                                report.add_nodes(path_node.error(exc))
                    else:
                        new_data[key] = recursive_process(data[key])

            elif isinstance(data, list):
                new_data = [
                    recursive_process(record) for record in data
                ]
            else:
                new_data = data
            return new_data
        print "DDD", data
        data = recursive_process(data)
        if report.count_failures():
            raise Exception(report.render())
        return data

    def validate_data_tree(self, data_tree):
        report = ReportNode(u"Data validation:")
        report.add_nodes(
            checks.check_fuel_ver_compatible_with_package_ver(
                self.minimal_fuel_version,
                data_tree
            )
        )
        report.add_nodes(
            checks.check_json_schema_is_valid(
                schemas.metadata_v5_0_0.metadata,
                data_tree
            )
        )
        for release in data_tree.get('releases', []):
            release_report = ReportNode(u'Checking release')
            for graph in release.get('graphs', []):
                release_report.info(u'Graph: "{}"'.format(
                    graph.get('type'))
                )
                release_report.add_nodes(
                    checks.check_json_schema_is_valid(
                        schema=schemas.graph_v5_0_0.graph,
                        data=graph
                    )
                )

            report.add_nodes(release_report)
        return report

    def validate(self, plugin_path=None):
        if plugin_path:
            self.plugin_path = plugin_path
        report = ReportNode(
            u"Validating plugin located at: {}".format(self.plugin_path)
        )
        data_tree = self.load_data_tree(self.plugin_path)
        report.info(u"Data loaded, validating data...")
        if not report.is_failed():
            report.add_nodes(
                self.validate_data_tree(data_tree)
            )
        return report
