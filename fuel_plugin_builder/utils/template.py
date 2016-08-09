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
import io
import logging
import os

from mako.template import Template

import fs_tools
import path_tools

logger = logging.getLogger(__name__)


def render_files_in_dir(dir_path, params):
    """Renders all *.mako files and removes templates

    :param str dir_path: path to the directory
    :param dict params: parameters for rendering
    """
    for root, _, files in os.walk(dir_path):
        for file_path in files:

            path_tools.normalize_extension()
            name, extension = os.path.splitext(file_path)
            if not extension == '.mako':
                continue

            src_path = os.path.join(root, file_path)
            dst_path = os.path.join(root, name)
            render_to_file(src_path, dst_path, params)
            fs_tools.copy_file_permissions(src_path, dst_path)
            fs_tools.remove(src_path)


def render_to_file(src, dst, params):
    """Render mako template and write it to specified file

    :param src: path to template
    :param dst: path where rendered template will be saved
    """
    logger.debug(u'Render template from {0} to {1} with params: {2}'.format(
        src, dst, params))

    # NOTE(aroma): we use io.open because sometimes we ended up with
    # non-ascii chars in rendered template so must explicitly
    # converse content to 'utf-8' encoding before writing

    with io.open(src, 'r', encoding='utf-8') as f:
        template_file = f.read()

    with io.open(dst, 'w', encoding='utf-8') as f:
        # NOTE(aroma): 'render' in such configuration always
        # return unicode object as the result
        rendered_file = Template(template_file).render(**params)
        f.write(rendered_file)
