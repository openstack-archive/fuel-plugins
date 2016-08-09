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

import io
import logging
import os

from mako.template import Template

from fuel_plugin_builder import consts
from fuel_plugin_builder.utils import fs

logger = logging.getLogger(__name__)


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
            load_template_and_render_to_file(src_path, dst_path, params)
            fs.copy_file_permissions(src_path, dst_path)
            fs.remove(src_path)


def render_template_file(src, **context):
    """Render Mako template to string.

    :param src: path to template
    :type src: str
    :param context: template engine context
    :type context: list|dict|None

    :return: string
    :rtype: str
    """
    with io.open(src, 'r', encoding=consts.DEFAULT_ENCODING) as f:
        template_file = f.read()
    rendered_file_content = Template(template_file).render(**context)
    return rendered_file_content


def load_template_and_render_to_file(src, dst, context):
    """Render Mako template and write it to specified file.

    :param src: path to template
    :type src: str
    :param dst: path where rendered template will be saved
    :type dst: str
    :param context: template engine context
    :type context: list|dict|None
    """
    logger.debug(u'Render template from {0} to {1} with params: {2}'.format(
        src, dst, context))

    with io.open(src, 'r', encoding=consts.DEFAULT_ENCODING) as f:
        template_file = f.read()
    with io.open(dst, 'w', encoding=consts.DEFAULT_ENCODING) as f:
        rendered_file = Template(template_file).render(**context)
        f.write(rendered_file)
