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

from fuel_plugin_builder import consts


import json
import yaml

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder import reports


def deserializer_json(raw_data, *args, **kwargs):
    """Load JSON data from file object.

    :param raw_data: raw data
    :type raw_data: basestring

    :return: data
    :rtype: list|dict
    """
    return json.load(raw_data, *args, **kwargs)


def deserializer_yaml(raw_data, loader=yaml.Loader, *args, **kwargs):
    """Load YAML data from file object.

    :param raw_data: raw data
    :type raw_data: basestring
    :param loader: YAML-specific loader
    :type loader: yaml.Loader

    :return: data
    :rtype: list|dict
    """
    result = yaml.load(raw_data, Loader=loader)
    return result


def deserializer_plaintext(raw_data, *args, **kwargs):
    """Load plaintext data from file object.

    Not doing anything except passing data throug.

    :param raw_data: text
    :type raw_data: basestring

    :return: data
    :rtype: list|dict
    """
    return raw_data


def serializer_json(data, *args, **kwargs):
    """Load JSON data from file object.

    :param data: data
    :type data: dict|list

    :return: raw data
    :rtype: basestring
    """
    return json.dumps(data, *args, **kwargs)


def serializer_yaml(data, dumper=yaml.SafeDumper, *args, **kwargs):
    """Load YAML data from file object.

    :param data: data
    :type data: dict|list
    :param dumper: YAML-specific dumper
    :type dumper: yaml.Dumper

    :return: data
    :rtype: basestring
    """
    return yaml.dump(data, Dumper=dumper, **kwargs)


def serializer_plaintext(cls, data, *args, **kwargs):
    """Serialize plaintext to string.

    Not doing anything except passing data throug.

    :param data: data
    :type data: basestring

    :return: data
    :rtype: basestring
    """
    return data


DESERIALIZERS = {
    "json": deserializer_json,
    "yaml": deserializer_yaml,
    "txt": deserializer_plaintext
}

SERIALIZERS = {
    "json": serializer_json,
    "yaml": serializer_yaml,
    "txt": serializer_plaintext
}


# All files loading and saving operations are recommended to be performed via
# FilesManager class
class FilesManager(object):
    """Files Manager is responsive for files loading and saving
    and including serialization and deserialization operations.

    It's recommended to work with FM using absolute paths.
    """

    def load(self, path, *args, **kwargs):
        """Load file from path.

        :param path: path
        :type path: str

        :return: data
        :rtype: list|dict
        """

        path = utils.fs.get_best_path_by_mask(path, list(DESERIALIZERS))
        ext = utils.fs.get_path_extension(path)
        deserializer = DESERIALIZERS.get(ext)

        if deserializer is not None:
            with open(path, 'r') as content_file:
                raw_content = content_file.read()
            return deserializer(raw_content, *args, **kwargs)
        else:
            raise errors.InvalidFileFormat(
                path,
                list(DESERIALIZERS)
            )

    def save(self, path, *args, **kwargs):
        """Save data to path applying serializer.

        :param path: full path with extension that will define serialization
                     format.
        :type path: str

        :return: data
        :rtype: list|dict
        """
        ext = utils.fs.get_path_extension(path)
        serializer = SERIALIZERS.get(ext)

        if serializer is not None:
            return serializer(path, *args, **kwargs)
        else:
            raise errors.InvalidFileFormat(path, list(SERIALIZERS))


class BaseLoader(object):
    """Loader deals with the file structure providing ability to load, combine
    and form the data tree from the plugin directory.

    If loader fails it raising exception with the report attached.
    """
    files_manager = FilesManager()
    plugin_path = None

    def __init__(self, plugin_path=None):
        self.plugin_path = plugin_path
        print "LOADER INIT", self.plugin_path

    def _get_absolute_path(self, path):
        """Get absolute path from the relative to the plugins folder.

        :param path: relative path
        :type path: str

        :return: path string
        :rtype: str
        """
        return os.path.join(self.plugin_path, path)

    @property
    def root_metadata_path(self):
        """Where is the root plugin data file located."""
        return self._get_absolute_path(consts.ROOT_FILE_NAME)

    def _load_root_metadata_file(self):
        """Get plugin root data (usually, it's metadata.yaml).

        :return: data
        :rtype: list|dict
        """
        print "Loading root metadata", self.root_metadata_path
        return self.files_manager.load(self.root_metadata_path)

    def load(self, plugin_path):
        """Loads data from the given plugin path and producing data tree
        that could be validated and used by Fuel business logic.

        :param plugin_path: plugin root path
        :param plugin_path: str|basestring

        :return: data tree starting from the data in root metadata file
        :rtype: tuple(dict, reports.ReportNode)
        """
        data = {}
        plugin_path = plugin_path or self.plugin_path
        report = reports.ReportNode(
            u"File structure validation: {}".format(plugin_path))
        try:
            data = self._load_root_metadata_file()
            report.info(u"Loading related files")
        except Exception as e:
            report.error(e)

        return data, report
