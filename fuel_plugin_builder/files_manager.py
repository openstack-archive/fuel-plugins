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

import json
import yaml

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils


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

    def is_dir(self, path):
        return utils.fs.get_best_path_by_mask(path)

    def load(self, path, *args, **kwargs):
        """Load file from path.

        :param path: path
        :type path: str

        :return: data
        :rtype: list|dict
        """

        path = utils.fs.get_best_path_by_mask(path)
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

        :param path: path
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

# Global export
files_manager = FilesManager()
