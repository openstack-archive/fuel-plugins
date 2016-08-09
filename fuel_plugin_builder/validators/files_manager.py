# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
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

import utils.path_tools
from fuel_plugin_builder import errors
from fuel_plugin_builder import utils


# All files operations should be done through this class

class FilesManager(object):
    """Converts files to data and back."""

    # file loading functions
    file_deserializers = {
        "json": json.load,
        "yaml": lambda f, loader=yaml.SafeLoader: yaml.load(f, Loader=loader)
    }

    # file loading functions
    file_serializers = {
        "json": json.dumps,
        "yaml": lambda f, dumper=yaml.SafeDumper: yaml.dump(f, Dumper=dumper)
    }

    def load(self, path, *args, **kwargs):
        """Load file from path.

        :param path: path
        :type path: str

        :return: data
        :rtype: list|dict
        """
        ext = utils.path_tools.get_path_extension(path)
        loader = files_manager.file_deserializers.get(ext)

        if loader is not None:
            return loader(path, *args, **kwargs)
        else:
            raise errors.InvalidFileFormat(
                path,
                list(self.file_deserializers)
            )

    def save(self, path, *args, **kwargs):
        """Save data to path applying serializer.

        :param path: path
        :type path: str

        :return: data
        :rtype: list|dict
        """
        ext = utils.path_tools.get_path_extension(path)
        saver = files_manager.file_serializers.get(ext)

        if saver is not None:
            return saver(path, *args, **kwargs)
        else:
            raise errors.InvalidFileFormat(
                path,
                list(self.file_serializers)
            )

# Global export
files_manager = FilesManager()
