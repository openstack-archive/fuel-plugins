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


import os
import logging

import subprocess

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
        path = path.strip('"')
        exe_file = os.path.join(path, cmd)
        if is_executable(exe_file):
            return exe_file

    return None


def exec_cmd(cmd):
    """Execute command with logging.
    Ouput of stdout and stderr will be written
    in log.

    :param cmd: shell command
    """
    logger.debug(u'Execute command "{0}"'.format(cmd))
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)

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
