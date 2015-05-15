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

import datetime
import hashlib
import logging
import os
import shutil
import subprocess
import tarfile
import yaml

from distutils import dir_util
from distutils.version import StrictVersion
from glob import glob

from mako.template import Template

from fuel_plugin_builder import errors

logger = logging.getLogger(__name__)


def is_executable(file_path):
    """Checks if file executable

    :param str file_path: path to the file
    :returns: True if file is executable, False if is not
    """
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def which(cmd):
    """Checks if file executable

    :param str cmd: the name of the command or path

    :returns: None if there is no such command,
              if there is such command returns
              the path to the command
    """

    fpath, fname = os.path.split(cmd)
    if fpath:
        if is_executable(cmd):
            return cmd

    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, cmd)
        if is_executable(exe_file):
            return exe_file

    return None


def exec_cmd(cmd, cwd=None):
    """Execute command with logging.
    Ouput of stdout and stderr will be written
    in log.

    :param cmd: shell command
    :param cwd: string or None
    """
    logger.debug(u'Execute command "{0}"'.format(cmd))
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=cwd)

    logger.debug(u'Stdout and stderr of command "{0}":'.format(cmd))
    for line in child.stdout:
        logger.debug(line.rstrip())

    child.wait()
    exit_code = child.returncode

    if exit_code != 0:
        raise errors.ExecutedErrorNonZeroExitCode(
            u'Shell command executed with "{0}" '
            'exit code: {1} '.format(exit_code, cmd))

    logger.debug(u'Command "{0}" successfully executed'.format(cmd))


def create_dir(dir_path):
    """Creates directory

    :param dir_path: directory path
    :raises: errors.DirectoryExistsError
    """
    logger.debug(u'Creating directory %s', dir_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def exists(path):
    """Checks if filel is exist

    :param str path: path to the file
    :returns: True if file is exist, Flase if is not
    """
    return os.path.lexists(path)


def basename(path):
    """Basename for path

    :param str path: path to the file
    :returns: str with filename
    """
    return os.path.basename(path)


def render_to_file(src, dst, params):
    """Render mako template and write it to specified file

    :param src: path to template
    :param dst: path where rendered template will be saved
    """
    logger.debug('Render template from {0} to {1} with params: {2}'.format(
        src, dst, params))
    with open(src, 'r') as f:
        template_file = f.read()

    with open(dst, 'w') as f:
        rendered_file = Template(template_file).render(**params)
        f.write(rendered_file)


def render_files_in_dir(dir_path, params):
    """Renders all *.mako files and removes templates

    :param str dir_path: path to the directory
    :param dict params: parameters for rendering
    """
    for root, _, files in os.walk(dir_path):
        for file_path in files:
            name, extension = os.path.splitext(file_path)
            if not extension == '.mako':
                continue

            src_path = os.path.join(root, file_path)
            dst_path = os.path.join(root, name)
            render_to_file(src_path, dst_path, params)
            copy_file_permissions(src_path, dst_path)
            remove(src_path)


def copy_file_permissions(src, dst):
    """Copies file permissions

    :param str src: source file
    :param str dst: destination
    """
    shutil.copymode(src, dst)


def remove(path):
    """Remove file or directory

    :param path: a file or directory to remove
    """
    logger.debug(u'Removing "%s"', path)

    if not os.path.lexists(path):
        return

    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


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
        dir_util.copy_tree(src, dst, preserve_symlinks=True)
    else:
        shutil.copy(src, dst)


def copy_files_in_dir(src, dst):
    """Copies file in directory

    :param str src: source files
    :param str dst: destination directory
    """
    logger.debug(u'Copy files in directory %s %s', src, dst)
    for f in glob(src):
        dst_path = os.path.join(dst, os.path.basename(f))
        copy(f, dst_path)


def move_files_in_dir(src, dst):
    """Move files or directories

    :param str src: source files or directories
    :param str dst: destination directory
    """
    logger.debug(u'Move files to directory %s %s', src, dst)
    for f in glob(src):
        dst_path = os.path.join(dst, os.path.basename(f))
        shutil.move(f, dst_path)


def make_tar_gz(dir_path, tar_path, files_prefix):
    """Compress the file in tar.gz archive

    :param str dir_path: directory for archiving
    :param str tar_path: the name and path to the file
    :param str files_prefix: the directory in the tar files where all
                             of the files are allocated
    """
    logger.debug(u'Archive directory %s to file %s', dir_path, tar_path)
    tar = tarfile.open(tar_path, 'w:gz')
    tar.add(dir_path, arcname=files_prefix)
    tar.close()


def parse_yaml(path):
    """Parses yaml file

    :param str path: path to the file
    :returns: dict or list
    """
    return yaml.load(open(path))


def calculate_sha(file_path, chunk_size=2 ** 20):
    """Calculate file's checksum

    :param str file_path: file path
    :param int chunk_size: optional parameter, size of chunk
    :returns: SHA1 string
    """
    sha = hashlib.sha1()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            sha.update(chunk)

    return sha.hexdigest()


def calculate_checksums(dir_path):
    """Calculates checksums of files in the directory

    :param str dir_path: path to the directory
    :returns: list of dicts, where 'checksum' is SHA1,
              'file_path' is a relative path to the file
    """
    checksums = []
    for root, _, files in os.walk(dir_path):
        for file_path in files:
            full_path = os.path.join(root, file_path)
            rel_path = os.path.relpath(full_path, dir_path)

            checksums.append({
                'checksum': calculate_sha(full_path),
                'file_path': rel_path})

    return checksums


def create_checksums_file(dir_path, checksums_file):
    """Creates file with checksums

    :param str dir_path: path to the directory for checksums calculation
    :param str checksums_file: path to the file where checksums are saved
    """
    checksums = calculate_checksums(dir_path)
    checksums_sorted = sorted(checksums, key=lambda c: c['file_path'])
    checksum_lines = [
        '{checksum} {file_path}\n'.format(**checksum)
        for checksum in checksums_sorted]

    with open(checksums_file, 'w') as f:
        f.writelines(checksum_lines)


def version_split_name_rpm(version):
    version_tuple = StrictVersion(version).version
    major = '.'.join(map(str, version_tuple[0:2]))
    minor = version

    return (major, minor)


def get_current_year():
    """Returns current year
    """
    return str(datetime.date.today().year)
