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
    for f in glob.glob(src):
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
    with tarfile.open(tar_path, consts.TAR_PARAMETERS) as tar:
        tar.add(dir_path, arcname=files_prefix)


def move_files_in_dir(src, dst):
    """Move files or directories.

    :param src: source files or directories
    :type src: str
    :param str dst: destination directory
    :type dst: str
    """
    logger.debug(u'Move files to directory %s %s', src, dst)
    for f in glob.glob(src):
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
    for f in glob.glob(mask):
        remove(f)
