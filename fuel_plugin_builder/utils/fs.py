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

import distutils
import glob
import logging
import os
import shutil
import subprocess
import tarfile


from fuel_plugin_builder import consts
from fuel_plugin_builder import errors

logger = logging.getLogger(__name__)


def copy(src, dst):
    """Copy a given file or directory from one place to another.
    Rewrite already exists files.

    :param src: copy from
    :param dst: copy to
    """
    logger.debug(u'Copy from %s to %s', src, dst)

    if os.path.isdir(src):
        # dir_util.copy_tree use here instead of shutil.copytree because
        # it can overwrite existing folder and files. This is necessary
        # for our template combinations, e.g.: base and v1
        distutils.dir_util.copy_tree(src, dst, preserve_symlinks=True)
    else:
        shutil.copy(src, dst)


def copy_file_permissions(src, dst):
    """Copies file permissions

    :param str src: source file
    :param str dst: destination
    """
    shutil.copymode(src, dst)


def copy_files_in_dir(src, dst):
    """Copies file in directory

    :param str src: source files
    :param str dst: destination directory
    """
    logger.debug(u'Copy files in directory %s %s', src, dst)
    for f in get_paths(src):
        dst_path = os.path.join(dst, os.path.basename(f))
        copy(f, dst_path)


def create_dir(dir_path):
    """Creates directory.

    :param dir_path: directory path
    :type dir_path: directory str
    :raises: errors.DirectoryExistsError
    """
    logger.debug(u'Creating directory %s', dir_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def exec_piped_cmds(cmds, cwd=None):
    """Execute pipe of commands with logging.

    :param cmds: list of shell commands
    :type cmds: list
    :param cwd: current working directory
    :type cwd: string or None
    """
    logger.debug(u'Executing commands "{0}"'.format(" | ".join(cmds)))

    std_out = None
    for cmd in cmds:
        child = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
            cwd=cwd)

        std_out, std_err = child.communicate(input=std_out)
        exit_code = child.returncode

        if exit_code != 0:
            logger.debug(u'Stderr of command "{0}":'.format(cmd))
            logger.debug(std_err)

            raise errors.ExecutedErrorNonZeroExitCode(
                u'Shell command executed with "{0}" '
                u'exit code: {1} '.format(exit_code, cmd))

    logger.debug(u'Stdout of command "{0}":'.format(" | ".join(cmds)))
    logger.debug(std_out)
    logger.debug(
        u'Command "{0}" successfully executed'.format(" | ".join(cmds))
    )


def make_tar_gz(dir_path, tar_path, files_prefix):
    """Compress the file in tar.gz archive.

    :param str dir_path: directory for archiving
    :type dir_path: str
    :param str tar_path: the name and path to the file
    :type tar_path: str
    :param str files_prefix: the directory in the tar files where all
                             of the files are allocated
    :type files_prefix: str
    """
    logger.debug(u'Archive directory %s to file %s', dir_path, tar_path)
    tar = tarfile.open(tar_path, 'w:gz')
    tar.add(dir_path, arcname=files_prefix)
    tar.close()


def move_files_in_dir(src, dst):
    """Move files or directories.

    :param src: source files or directories
    :type src: str
    :param str dst: destination directory
    :type dst: str
    """
    logger.debug(u'Move files to directory %s %s', src, dst)
    for f in get_paths(src):
        dst_path = os.path.join(dst, os.path.basename(f))
        shutil.move(f, dst_path)


def remove(path):
    """Remove file or directory.

    :param path: a file or directory to remove
    :type path: str
    """
    logger.debug(u'Removing "%s"', path)

    if not os.path.lexists(path):
        return

    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def remove_by_mask(mask):
    """Deletes files by mask.

    :param mask: files mask
    :type mask: str
    """
    logger.debug(u'Remove files by mask %s', mask)
    for f in get_paths(mask):
        remove(f)


def get_best_path_by_mask(path_mask, allowed_formats=None):
    """Find acceptable file defined by glob respecting allowed formats.

    Final file path will be chosen by format in available_formats as close to
    first one enlisted as possible. So the order of allowed_formats and
    const.SUPPORTED_FORMATS is important.

    :param path_mask: path mask like ./my-file.*
    :type path_mask: str

    :param allowed_formats: available file formats
    :type allowed_formats: iterable

    :return: path to file
    :rtype: str
    """

    allowed_formats = allowed_formats or consts.SUPPORTED_FORMATS

    for path in get_paths(path_mask):
        try:
            extension = get_path_extension(path)
        except KeyError:
            continue

        if extension in allowed_formats:
            return path

    raise errors.FilesInPathDoesNotExist(
        u"Can't find appropriate file with mask {} "
        u"Ensure that file is on its place or use one of the following file "
        u"formats: {}.".format(
            path_mask,
            u", ".join(list(allowed_formats))
        )
    )


def get_paths(path_mask):
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


def is_file(path):
    """Checks if path is file.

    :param path: path
    :type path: str

    :returns: True if given path is file, False if is not
    :rtype: bool
    """
    return os.path.isfile(path)


def is_dir(path):
    """Checks if path is directory.

    :param path: path
    :type path: str

    :returns: True if given path is directory, False if is not
    :rtype: bool
    """
    return os.path.isdir(path)


def is_executable(file_path):
    """Checks if file executable.

    :param file_path: path to the file
    :type file_path: str

    :returns: True if file is executable, False if is not
    :rtype: bool
    """
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def which(cmd):
    """Checks cmd location.

    :param cmd: the name of the command or path
    :type cmd: str

    :returns: None if there is no such command, if there is such command
              returns the path to the command
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
    return extension.lower()


def get_path_without_extension(path):
    """Return path without extension.

    Example:
    > /var/config/template.yaml.mako -> /var/config/template.yaml
    > /var/config/template.yaml -> /var/config/template
    > /var/config/template -> /var/config/template

    :param path: path
    :type path: str

    :return: path without extension
    :rtype: str|None
    """
    if path:
        return os.path.splitext(path)[0]
    else:
        return None


def get_path_extension(path):
    """Get extensions from path.

    :param path: path
    :type path: str
    :return: normalized extension
    :rtype: str
    """
    return normalize_extension(os.path.splitext(path)[1])
