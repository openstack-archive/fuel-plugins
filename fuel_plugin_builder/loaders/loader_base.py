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

import os

import six

import errors
import reports
import utils
from files_manager import FilesManager
from fuel_plugin_builder import consts


class LoaderBase(object):
    """Loader deals with the file structure providing ability to load, combine
    and form the data tree from the plugin directory.

    If loader fails it raising exception with the report attached.
    """

    _path_suffix = consts.PATHS_SUFFIX

    def __init__(self, plugin_path=None):
        self.files_manager = FilesManager()
        self.plugin_path = plugin_path

    _map_paths_to_data_keys = {}

    def _get_absolute_path(self, path):
        """Get absolute path from the relative to the plugins folder.

        :param path: relative path
        :type path: str

        :return: path string
        :rtype: str
        """
        return os.path.join(self.plugin_path, path)

    @property
    def _root_metadata_path(self):
        """Where is the root plugin data file located."""
        return self._get_absolute_path(consts.ROOT_FILE_NAME)

    def _recursive_process_paths(self, data, report):
        """Recursively processed nested list/dict.

        :param data: data
        :type data: iterable

        :param report: report node
        :type report: reports.ReportNode

        :returns: data
        :rtype: list|dict
        """
        if isinstance(data, dict):
            new_data = {}
            for key in tuple(data):
                value = data[key]
                # if we have key with path we could do 3 things:
                #
                # * if it is pointing to directory, check dir existence and
                #   leave path intact
                #
                # * if it is a `glob` compatible mask, iterate over files
                #   that are matched this mask and compatible with
                #   FileManager then merge the result.
                #   Then remove _path suffix from key.
                #
                # * if it is file compatible with FileManager, read this
                #   file and remove _path suffix from key.
                if key.endswith(self._path_suffix) \
                        and isinstance(value, six.string_types):
                    if utils.is_dir(self._get_absolute_path(value)):
                        report.info(u"{} is valid directory".format(
                            value))
                        # leave directories as is
                        new_data[key] = value
                    else:
                        cleaned_key = key[:- len(self._path_suffix)]
                        try:
                            loaded_data = self.files_manager.load(
                                self._get_absolute_path(value)
                            )
                            new_data[cleaned_key] = loaded_data
                        except Exception as exc:
                            path_node = reports.ReportNode(data[key])
                            report.add_nodes(path_node.error(exc))
                            # keep path as is
                            new_data[key] = value

                else:
                    new_data[key] = self._recursive_process_paths(
                        data[key], report)

        elif isinstance(data, list):
            new_data = [
                self._recursive_process_paths(record, report)
                for record in data
            ]
        else:
            new_data = data
        return new_data

    def _load_root_metadata_file(self):
        """Get plugin root data (usually, it's metadata.yaml).

        :return: data
        :rtype: list|dict
        """
        report = reports.ReportNode(u"Loading root metadata file:{}".format(
            self._root_metadata_path
        ))
        try:
            data = self.files_manager.load(self._root_metadata_path)
        except Exception as exc:
            report.error(exc)
            return {}, report   # nothing to do anymore
        data = self._recursive_process_paths(data, report)
        return data, report

    def load(self, plugin_path=None):
        """Loads data from the given plugin path and producing data tree
        that could be validated and used by Fuel business logic.

        :param plugin_path: plugin root path
        :param plugin_path: str|basestring|None

        :return: data tree starting from the data in root metadata file
        :rtype: tuple(dict, reports.ReportNode)
        """
        plugin_path = plugin_path or self.plugin_path
        report = reports.ReportNode(
            u"File structure validation: {}".format(plugin_path))
        data, root_report = self._load_root_metadata_file()
        report.add_nodes(root_report)

        # load files with fixed location
        for key, file_path in six.iteritems(self._map_paths_to_data_keys):
            file_report = reports.ReportNode(file_path)

            try:
                data[key] = self.files_manager.load(
                    self._get_absolute_path(file_path)
                )
            except Exception as exc:
                file_report.info(exc.message)
                report.add_nodes(file_report)
        return data, report
