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
from fuel_plugin_builder.reports import ReportNode
from fuel_plugin_builder import utils
from base import BaseLoader


class LoaderV5(BaseLoader):
    path_suffix = consts.PATHS_SUFFIX

    def load(self, plugin_path=None):
        """See BaseLoader documentation."""
        data, report = super(LoaderV5, self).load(plugin_path)
        try:
            data = self._load_root_metadata_file()
        except Exception as e:
            report.error(e)

        report.info(u"Loading related files")

        def recursive_process(data):
            """Recursively processed nested list/dict.

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
                    if key.endswith(self.path_suffix) \
                            and isinstance(value, six.string_types):
                        if utils.fs.is_dir(self._get_absolute_path(value)):
                            report.info(u"{} is valid directory".format(
                                value))
                            # leave directories as is
                            new_data[key] = value
                        else:
                            cleaned_key = key[:- len(self.path_suffix)]
                            try:
                                loaded_data = self.files_manager.load(
                                    self._get_absolute_path(value)
                                )
                                new_data[cleaned_key] = loaded_data
                            except Exception as exc:
                                path_node = ReportNode(data[key])
                                report.add_nodes(path_node.error(exc))
                                # keep path as is
                                new_data[key] = value

                    else:
                        new_data[key] = recursive_process(data[key])

            elif isinstance(data, list):
                new_data = [
                    recursive_process(record) for record in data
                    ]
            else:
                new_data = data
            return new_data

        data = recursive_process(data)
        return data, report
