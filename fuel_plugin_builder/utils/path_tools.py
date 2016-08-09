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
import glob
import os

import fs_tools

from fuel_plugin_builder import consts
from fuel_plugin_builder import errors


def get_best_path_by_mask(path_mask, available_formats=None):
    """Find acceptable file by mask respecting specified file formats
     formats.

    :param path_mask: path mask like ./my-file.*
    :type path_mask: str

    :param available_formats: available file formats
    :type available_formats: iterable

    :return: path to file
    :rtype str:
    """

    available_formats = available_formats or consts.SUPPORTED_FORMATS

    for path in get_paths_by_mask(path_mask):
        result = {}
        try:
            extension = utils.path_tools.get_path_extension(path)
        except KeyError:
            continue

        if extension in available_formats:
            if result.get(extension):
                return result.get(extension)

        raise IOError(
            "Unsupported file format {}\n"
            "Use one of: {}".format(
                path,
                ", ".join(list(available_formats))
            )
        )


def get_paths_by_mask(path_mask):
    """Returns glob(bed) files list.

    :param path_mask:
    :type path_mask: str
    :return: list of paths
    :rtype: str
    """
    return glob.glob(path_mask)


def is_exists(path):
    """Checks if path is exists.

    :param path: path to the file
    :type path: str
    :returns: True if file is exist, Flase if is not
    """
    return os.path.lexists(path)


def is_dir(path):
    """Checks if path is directory.

    :param path: path
    :type path: str
    """
    return os.path.isdir(path)


def is_executable(cmd):
    """Checks if file executable.

    Taken from: http://stackoverflow.com/a/377028/439466

    :param cmd: the name of the command or path
    :type cmd: str
    :returns: None if there is no such command,
              if there is such command returns
              the path to the command
    :rtype: None|str
    """

    file_path, file_name = os.path.split(cmd)
    if file_path:
        if is_executable(cmd):
            return cmd

    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, cmd)
        if is_executable(exe_file):
            return exe_file

    return None


def is_file(path):
    """Checks if path is file.

    :param path: path
    :type path: string
    """
    return os.path.isfile(path)


def basename(path):
    """Basename for path

    :param str path: path to the file
    :returns: str with filename
    """
    return os.path.basename(path)


def files_in_path(path, follow_links=False):
    """Walks dir and return list of found files or list with given path if
    given path is not a folder.

    :param follow_links: follow links while walking
    :type follow_links: bool
    :param path: path
    :type path: str
    :return: list of file paths
    :rtype: list[str]
    """
    matches = []
    if os.path.exists(path):
        if os.path.isdir(path):
            for root, dir_names, file_names in os.walk(
                    path, followlinks=follow_links):
                for filename in file_names:
                    matches.append(os.path.join(root, filename))
        else:
            matches.append(path)
    return matches


def normalize_extension(extension):
    """Normalize extension.

    examples:
    > ".JSON" -> "json"
    > ".yaml" -> "yaml"
    > "CSV" -> "csv"
    > "intact" -> "intact"
    > "." -> InvalidFileExtension
    > "" -> InvalidFileExtension

    :param extension: extension
    :type extension: str

    :return: normalised extension
    :rtype: str
    """
    if extension:
        if extension[0] == '.':
            extension = extension[1:]
    if not extension:
        raise errors.InvalidFileExtension(
            "Invalid file extension: {}".format(extension)
        )
    return extension.lower()


def get_path_extension(path):
    """Get extensions from path.

    :param path: path
    :type path: str
    :return: normalized extension
    :rtype str:
    """
    return path_tools.normalize_extension(os.path.splitext(path)[1])