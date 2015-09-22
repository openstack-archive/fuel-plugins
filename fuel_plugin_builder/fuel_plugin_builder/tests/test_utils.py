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
import shutil
import subprocess
import tempfile

import mock
from mock import patch

from fuel_plugin_builder import errors
from fuel_plugin_builder.tests.base import BaseTestCase
from fuel_plugin_builder.tests.base import FakeFile
from fuel_plugin_builder import utils


class TestUtils(BaseTestCase):

    @mock.patch('fuel_plugin_builder.utils.os.path.isfile', return_value=True)
    @mock.patch('fuel_plugin_builder.utils.os.access', return_value=True)
    def test_is_executable_returns_true(self, access_mock, isfile_mock):
        file_name = 'file_name'
        self.assertTrue(utils.is_executable(file_name))
        isfile_mock.assert_called_once_with(file_name)
        access_mock.assert_called_once_with(file_name, os.X_OK)

    @mock.patch('fuel_plugin_builder.utils.os.path.isfile', return_value=True)
    @mock.patch('fuel_plugin_builder.utils.os.access', return_value=False)
    def test_is_executable_returns_false(self, access_mock, isfile_mock):
        file_name = 'file_name'
        self.assertFalse(utils.is_executable(file_name))
        isfile_mock.assert_called_once_with(file_name)
        access_mock.assert_called_once_with(file_name, os.X_OK)

    @mock.patch('fuel_plugin_builder.utils.os')
    @mock.patch('fuel_plugin_builder.utils.is_executable', return_value=True)
    def test_which_returns_for_absolute_path_exec(self, _, os_mock):
        path = '/usr/bin/some_exec'
        os_mock.path.split.return_value = ('/usr/bin/', 'some_exec')
        self.assertEqual(utils.which(path), path)

    @mock.patch('fuel_plugin_builder.utils.is_executable',
                side_effect=[False, True])
    def test_which_returns_if_exec_in_env_path(self, _):
        # some_exec is in /bin directory
        path = 'some_exec'
        with patch.dict('os.environ', {'PATH': '/usr/bin:/bin'}):
            self.assertEqual(utils.which(path), '/bin/some_exec')

    @mock.patch('fuel_plugin_builder.utils.is_executable', return_value=False)
    def test_which_returns_none(self, _):
        with patch.dict('os.environ', {'PATH': '/usr/bin:/bin'}):
            self.assertIsNone(utils.which('some_exec'))

    def make_process_mock(self, return_code=0):
        process_mock = mock.Mock(
            communicate=mock.Mock(return_value=('stdout', 'stderr')))
        process_mock.stdout = ['Stdout line 1', 'Stdout line 2']
        process_mock.returncode = return_code

        return process_mock

    def test_exec_cmd_raises_error_in_case_of_non_zero_exit_code(self):
        cmd = 'some command'
        return_code = 1

        process_mock = self.make_process_mock(return_code=return_code)
        with patch.object(subprocess, 'Popen', return_value=process_mock):
            self.assertRaisesRegexp(
                errors.ExecutedErrorNonZeroExitCode,
                'Shell command executed with "{0}" '
                'exit code: {1} '.format(return_code, cmd),
                utils.exec_cmd, cmd)

    def test_exec_piped_cmds_raises_error_in_case_of_non_zero_exit_code(self):
        cmds = ['some command', 'some other command']
        return_code = 1

        process_mock = self.make_process_mock(return_code=return_code)
        with patch.object(subprocess, 'Popen', return_value=process_mock):
            self.assertRaisesRegexp(
                errors.ExecutedErrorNonZeroExitCode,
                'Shell command executed with "{0}" '
                'exit code: {1} '.format(return_code, " | ".join(cmds)),
                utils.exec_piped_cmds, cmds)

    def test_exec_cmd(self):
        process_mock = self.make_process_mock(return_code=0)
        with patch.object(subprocess, 'Popen', return_value=process_mock):
            utils.exec_cmd('some command')
            process_mock.wait.assert_called_once_with()

    def test_exec_piped_cmds(self):
        process_mock = self.make_process_mock(return_code=0)
        with patch.object(subprocess, 'Popen', return_value=process_mock):
            utils.exec_piped_cmds(['some command', 'some other command'])
            process_mock.communicate.assert_called_with(input='stdout')

    @mock.patch('fuel_plugin_builder.utils.os')
    def test_create_dir(self, os_mock):
        path = '/dir/path'
        os_mock.path.isdir.return_value = False
        utils.create_dir(path)
        os_mock.path.isdir.assert_called_once_with(path)
        os_mock.makedirs.assert_called_once_with(path)

    @mock.patch('fuel_plugin_builder.utils.os')
    def test_create_dir_dont_create_if_created(self, os_mock):
        path = '/dir/path'
        os_mock.path.isdir.return_value = True
        utils.create_dir(path)
        os_mock.path.isdir.assert_called_once_with(path)
        self.method_was_not_called(os_mock.makedirs)

    @mock.patch('fuel_plugin_builder.utils.os.path.lexists', return_value=True)
    def test_exists(self, os_exists):
        file_path = '/dir/path'
        self.assertTrue(utils.exists(file_path))
        os_exists.assert_called_once_with(file_path)

    @mock.patch('fuel_plugin_builder.utils.os.path.lexists',
                return_value=False)
    def test_exists_returns_false(self, os_exists):
        file_path = '/dir/path'
        self.assertFalse(utils.exists(file_path))
        os_exists.assert_called_once_with(file_path)

    @mock.patch('fuel_plugin_builder.utils.os.path.basename')
    def test_basename(self, base_mock):
        path = 'some_path'
        base_mock.return_value = path
        self.assertEqual(utils.basename(path), path)
        base_mock.assert_called_once_with(path)

    @mock.patch('fuel_plugin_builder.utils.shutil')
    def test_copy_file_permissions(self, shutil_mock):
        utils.copy_file_permissions('src', 'dst')
        shutil_mock.copymode.assert_called_once_with('src', 'dst')

    @mock.patch('fuel_plugin_builder.utils.shutil')
    @mock.patch('fuel_plugin_builder.utils.os')
    def test_remove_file(self, os_mock, shutil_mock):
        path = 'file_for_removing'
        os_mock.path.isdir.return_value = False
        utils.remove(path)
        os_mock.remove.assert_called_once_with(path)
        self.method_was_not_called(shutil_mock.rmtree)

    @mock.patch('fuel_plugin_builder.utils.shutil')
    @mock.patch('fuel_plugin_builder.utils.os')
    def test_remove_dir(self, os_mock, shutil_mock):
        path = 'dir_for_removing'
        os_mock.path.isdir.return_value = True
        os_mock.path.islink.return_value = False
        utils.remove(path)
        shutil_mock.rmtree.assert_called_once_with(path)
        self.method_was_not_called(os_mock.remove)

    @mock.patch('fuel_plugin_builder.utils.dir_util')
    @mock.patch('fuel_plugin_builder.utils.shutil')
    @mock.patch('fuel_plugin_builder.utils.os')
    def test_copy_file(self, os_mock, shutil_mock, dir_util_mock):
        src = '/tmp/soruce_file'
        dst = '/tmp/destination_file'
        os_mock.path.isdir.return_value = False
        utils.copy(src, dst)
        shutil_mock.copy.assert_called_once_with(src, dst)
        self.method_was_not_called(dir_util_mock.copy_tree)

    @mock.patch('fuel_plugin_builder.utils.dir_util')
    @mock.patch('fuel_plugin_builder.utils.shutil')
    @mock.patch('fuel_plugin_builder.utils.os')
    def test_copy_dir(self, os_mock, shutil_mock, dir_util_mock):
        src = '/tmp/soruce_file'
        dst = '/tmp/destination_file'
        os_mock.path.isdir.return_value = True
        utils.copy(src, dst)
        dir_util_mock.copy_tree.assert_called_once_with(
            src,
            dst,
            preserve_symlinks=True)
        self.method_was_not_called(shutil_mock.copy)

    @mock.patch('fuel_plugin_builder.utils.copy')
    @mock.patch('fuel_plugin_builder.utils.glob',
                return_value=['file1', 'file2'])
    def test_copy_files_in_dir(self, glob_mock, copy_mock):
        mask = 'file*'
        dst_dir = '/tmp'
        utils.copy_files_in_dir(mask, dst_dir)
        glob_mock.assert_called_once_with(mask)
        self.assertEqual(
            copy_mock.call_args_list,
            [mock.call('file1', '/tmp/file1'),
             mock.call('file2', '/tmp/file2')])

    @mock.patch('fuel_plugin_builder.utils.tarfile')
    def test_make_tar_gz(self, tarfile_mock):
        src = 'dir'
        dst = '/tmp/file.fp'
        prefix = 'prefix_dir'
        tar_mock = mock.MagicMock()
        tarfile_mock.open.return_value = tar_mock
        utils.make_tar_gz(src, dst, prefix)
        tarfile_mock.open.assert_called_once_with(dst, 'w:gz')
        tar_mock.add.assert_called_once_with(src, arcname=prefix)
        tar_mock.close.assert_called_once_with()

    @mock.patch('fuel_plugin_builder.utils.shutil.move')
    @mock.patch('fuel_plugin_builder.utils.glob',
                return_value=['file1', 'file2'])
    def test_move_files_in_dir(self, glob_mock, move_mock):
        mask = 'file*'
        dst_dir = '/tmp'
        utils.move_files_in_dir(mask, dst_dir)
        glob_mock.assert_called_once_with(mask)
        self.assertEqual(
            move_mock.call_args_list,
            [mock.call('file1', '/tmp/file1'),
             mock.call('file2', '/tmp/file2')])

    @mock.patch('__builtin__.open')
    @mock.patch('fuel_plugin_builder.utils.yaml')
    def test_parse_yaml(self, yaml_mock, open_mock):
        path = '/tmp/path'
        file_mock = mock.MagicMock()
        open_mock.return_value = file_mock
        utils.parse_yaml(path)
        open_mock.assert_called_once_with(path)
        yaml_mock.load.assert_called_once_with(file_mock)

    def test_render_to_file_unicode_handling(self):
        expected = u'тест'
        params = {'vendors': expected}
        template_content = "${vendors}"

        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir)

        src_file = os.path.join(temp_dir, 'test_template')
        dst_file = os.path.join(temp_dir, 'test_rendered')

        with open(src_file, 'w') as f:
            f.write(template_content)

        utils.render_to_file(src=src_file, dst=dst_file, params=params)

        with open(dst_file, 'rb') as f:
            actual = f.read()
            self.assertEqual(expected, actual.decode('utf-8'))

    @mock.patch('fuel_plugin_builder.utils.copy_file_permissions')
    @mock.patch('fuel_plugin_builder.utils.render_to_file')
    @mock.patch('fuel_plugin_builder.utils.remove')
    @mock.patch('fuel_plugin_builder.utils.os.walk')
    def test_render_files_in_dir(
            self, walk_mock, remove_mock, render_mock, copy_permissions_mock):
        dir_path = '/tmp/some_plugin'
        walk_mock.return_value = [
            [dir_path, '', ['file1.txt.mako', 'file2.txt']],
            [dir_path, '', ['file3', 'file4.mako']]]
        params = {'param1': 'value1', 'param2': 'value2'}

        utils.render_files_in_dir(dir_path, params)

        self.assertEqual(
            [mock.call('/tmp/some_plugin/file1.txt.mako',
                       '/tmp/some_plugin/file1.txt',
                       params),
             mock.call('/tmp/some_plugin/file4.mako',
                       '/tmp/some_plugin/file4',
                       params)],
            render_mock.call_args_list)

        self.assertEqual(
            [mock.call('/tmp/some_plugin/file1.txt.mako'),
             mock.call('/tmp/some_plugin/file4.mako')],
            remove_mock.call_args_list)

        self.assertEqual(
            [mock.call('/tmp/some_plugin/file1.txt.mako',
                       '/tmp/some_plugin/file1.txt'),
             mock.call('/tmp/some_plugin/file4.mako',
                       '/tmp/some_plugin/file4')],
            copy_permissions_mock.call_args_list)

    def test_calculate_sha(self):
        file_path = '/tmp/file'

        with mock.patch('__builtin__.open',
                        self.mock_open('fake file content')):

            self.assertEqual(
                utils.calculate_sha(file_path),
                '5083c27641e7e4ae287d690cb3fafb4dd6e8f6ab')

    @mock.patch('fuel_plugin_builder.utils.calculate_sha')
    @mock.patch('fuel_plugin_builder.utils.os.walk')
    def test_calculate_checksums(self, walk_mock, sha_mock):
        dir_path = '/tmp/dir_path'
        walk_mock.return_value = [
            [dir_path, '', ['file1.txt', 'file2.txt']],
            [dir_path, '', ['file3.txt']]]

        sha_mock.side_effect = ['sha_1', 'sha_2', 'sha_3']

        self.assertEqual(
            utils.calculate_checksums(dir_path),
            [{'file_path': 'file1.txt', 'checksum': 'sha_1'},
             {'file_path': 'file2.txt', 'checksum': 'sha_2'},
             {'file_path': 'file3.txt', 'checksum': 'sha_3'}])

        self.assertEqual(
            [mock.call('/tmp/dir_path/file1.txt'),
             mock.call('/tmp/dir_path/file2.txt'),
             mock.call('/tmp/dir_path/file3.txt')],
            sha_mock.call_args_list)

    @mock.patch('fuel_plugin_builder.utils.calculate_checksums')
    def test_create_checksums_file(self, calculate_mock):
        calculate_mock.return_value = [
            {'checksum': 'checksum2', 'file_path': 'file2.txt'},
            {'checksum': 'checksum', 'file_path': 'file1.txt'}]

        fileobj = FakeFile('')
        open_mock = mock.MagicMock(return_value=fileobj)

        with mock.patch('__builtin__.open', open_mock):
            utils.create_checksums_file('/tmp/dir', '/tmp/checksums')

        self.assertEqual(
            fileobj.getvalue(),
            'checksum file1.txt\nchecksum2 file2.txt\n')

    @mock.patch('fuel_plugin_builder.utils.remove')
    @mock.patch('fuel_plugin_builder.utils.glob',
                return_value=['file1', 'file2'])
    def test_remove_by_mask(self, glob_mock, remove_mock):
        mask = '/tmp/test/*.yaml'
        utils.remove_by_mask(mask)
        glob_mock.assert_called_once_with(mask)
        self.assertEqual(
            remove_mock.call_args_list,
            [mock.call('file1'), mock.call('file2')])

    @mock.patch('fuel_plugin_builder.utils.exists',
                return_value=True)
    def test_read_if_exist(self, utils_exists):
        file_path = '/tmp/file'
        with mock.patch('__builtin__.open', self.mock_open("foo")):
            self.assertEqual(utils.read_if_exist(file_path), "foo")
        utils_exists.assert_called_once_with(file_path)

    @mock.patch('fuel_plugin_builder.utils.exists',
                return_value=False)
    def test_read_if_exist_returns_empty(self, utils_exists):
        file_path = '/tmp/file'
        with mock.patch('__builtin__.open', self.mock_open("foo")):
            self.assertEqual(utils.read_if_exist(file_path), "")
        utils_exists.assert_called_once_with(file_path)
