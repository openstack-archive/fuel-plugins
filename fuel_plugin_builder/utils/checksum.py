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

import hashlib
import os


def calculate_file_sha(file_path, chunk_size=2 ** 20):
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


def calculate_file_checksums(dir_path):
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
                'checksum': calculate_file_sha(full_path),
                'file_path': rel_path})

    return checksums


def create_checksums_file(dir_path, checksums_file):
    """Creates file with checksums

    :param dir_path: path to the directory for checksums calculation
    :type dir_path: str
    :param checksums_file: path to the file where checksums are saved
    :type checksums_file: str
    """
    checksums = calculate_file_checksums(dir_path)
    checksums_sorted = sorted(checksums, key=lambda c: c['file_path'])
    checksum_lines = [
        '{checksum} {file_path}\n'.format(**checksum)
        for checksum in checksums_sorted]

    with open(checksums_file, 'w') as f:
        f.writelines(checksum_lines)
