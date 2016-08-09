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

import datetime
import json
import traceback

import six
import yaml

from fuel_plugin_builder.utils.data_structures import Enum


class DataWithReport(object):
    """Incapsulates result list/dict and report as property."""

    def __init__(self, seq=None, report=None, **kwargs):
        """Initialize DataWithReport.

        :param seq:
        :type seq: iterable|None
        :param report: report node
        :param report: ReportNode|None

        :returns: extended list or dict
        :rtype: DictResultWithReport|ListResultWithReport
        """
        super(DataWithReport, self).__init__(seq, **kwargs)
        self.report = report or ReportNode(u'No report provided')


class DictResultWithReport(DataWithReport, dict):
    pass


class ListResultWithReport(DataWithReport, list):
    pass


class TextReportConfig(object):
    indent_size = 4
    failure_pointer = '> '
    line_delimiter = '\n'

    def __init__(self, **kwargs):
        # update only already defined attributes
        for k in kwargs:
            if self.__getattribute__(k) and kwargs.get(k, None) is not None:
                self.__setattr__(k, kwargs[k])


class ReportNode(object):
    """Basic unit of Reports tree.

    Any ReportNode could be rendered as report with all children tree.
    """

    REPORT_LEVELS = Enum(
        'error',
        'warning',
        'info',
        'debug'
    )

    RENDER_FORMATS = Enum(
        'text',
        'json',
        'yaml'
    )

    text_report_config = TextReportConfig()
    # Size of the new level text indent when rendering report

    text = None
    level = None
    children = None
    time = None
    failed = False

    @property
    def _renderers(self):
        return {
            self.RENDER_FORMATS.text: self._render_text,
            self.RENDER_FORMATS.yaml: self._render_yaml,
            self.RENDER_FORMATS.json: self._render_json
        }

    def __init__(self,
                 text=None,
                 level=None,
                 children=None,
                 time=None,
                 failed=None):
        """Basic unit of report tree.

        :param text: node text
        :type text: str|basestring
        :param level: message level
        :type level: str|basestring
        :param children: list of child ReportNodes
        :type children: list[ReportNode]
        :param time: override node creation time
        :type time: datetime.datetime
        :param failed: failure flag that affects rendering
        :type failed: boolean
        """
        self.text = self._format_message_content(text)
        self.time = time or datetime.datetime.now()
        self.children = children if children is not None else []
        self.level = level or self.level
        if self.level == self.REPORT_LEVELS.error:
            self.failed = True
        if failed is not None:
            self.failed = failed

    def _render_json(self, depth=0, *args, **kwargs):
        next_level = depth + 1
        result = {}
        if self.text:
            result['text'] = self.text
        if self.level:
            result['level'] = self.level
        if self.time:
            result['time'] = self.time
        if len(self.children):
            result['children'] = [
                child._render_yaml(next_level, *args, **kwargs)
                for child in self.children]
        if depth > 0:
            return result
        else:
            return json.dumps(result, *args, **kwargs)

    def _render_yaml(self, depth=0, *args, **kwargs):
        next_level = depth + 1
        result = {}
        if self.text:
            result['text'] = self.text
        if self.level:
            result['level'] = self.level
        if self.time:
            result['time'] = self.time
        if len(self.children):
            result['children'] = [
                child._render_yaml(next_level, *args, **kwargs)
                for child in self.children]

        if depth > 0:
            return result
        else:
            return yaml.safe_dump(result, *args, **kwargs)

    def _render_text(self, depth=None, config=None):

        config = config if config else self.text_report_config
        indent = config.indent_size * (depth or 0) * ' '
        error_indent_size = max(
            len(indent) - len(config.failure_pointer),
            0
        )
        error_indent = error_indent_size * ' '

        lines = []
        failed = self.failed

        for child in self.children:
            child_lines = child._render_text(
                0 if depth is None else depth + 1,
                config=config)
            lines.extend(child_lines)

        def _make_level_string(string):
            return '{}: '.format(string.upper()) if string else ''

        if self.text or self.level:
            output = '{indent}{pointer}{text}'.format(
                indent=error_indent if failed else indent,
                pointer=config.failure_pointer if failed else '',
                text='{level}{text}'.format(
                    level=_make_level_string(self.level),
                    text=self.text or ''
                )
            )
            lines.insert(0, output)

        if depth is None:
            return config.line_delimiter.join(lines)
        else:
            return lines

    @staticmethod
    def _format_message_content(msg_or_exc):
        if not msg_or_exc:
            return msg_or_exc
        if isinstance(msg_or_exc, six.string_types):
            return msg_or_exc
        elif isinstance(msg_or_exc, Exception):
            tb = traceback.format_exc(msg_or_exc)
            return msg_or_exc.message or repr(msg_or_exc + (tb or ''))
        else:
            return "{}".format(msg_or_exc)

    def _attach_message(self, msg_or_exc, level, *args, **kwargs):
        self.add_nodes(
            ReportNode(self._format_message_content(msg_or_exc), level)
        )
        self.add_nodes(
            *(
                ReportNode(arg, level=self.level)
                for arg in args
            )
        )
        self.add_nodes(
            *(
                ReportNode(u'{}: {}'.format(key, kwargs[key]))
                for key in kwargs
            )
        )
        return self

    def add_nodes(self, *nodes):
        """Add single node or several nodes.

        :param nodes: one or several report nodes
        :type nodes: list[ReportNode]
        :raises: InspectionConfigurationError
        """
        for node in nodes:
            self.children.append(node)
        return self

    def error(self, msg_or_exc, *args, **kwargs):
        """Add child ReportNode with error message.

        :param msg_or_exc: message or exception
        :type msg_or_exc: str|basestring|Exception

        :return: self
        :rtype: ReportNode
        """
        return self._attach_message(
            msg_or_exc=msg_or_exc,
            level=self.REPORT_LEVELS.error,
            *args, **kwargs
        )

    def warning(self, msg_or_exc, *args, **kwargs):
        """Add child ReportNode with warning message.

        :param msg_or_exc: message or exception
        :type msg_or_exc: str|basestring|Exception

        :return: self
        :rtype: ReportNode
        """
        return self._attach_message(
            msg_or_exc=msg_or_exc,
            level=self.REPORT_LEVELS.warning,
            *args, **kwargs
        )

    def warn(self, msg_or_exc, *args, **kwargs):
        """Alias to warning."""
        return self.warning(msg_or_exc, *args, **kwargs)

    def info(self, msg_or_exc, *args, **kwargs):
        """Add child ReportNode with info message.

        :param msg_or_exc: message or exception
        :type msg_or_exc: str|basestring|Exception

        :return: self
        :rtype: ReportNode
        """
        return self._attach_message(
            msg_or_exc=msg_or_exc,
            level=self.REPORT_LEVELS.info,
            *args, **kwargs
        )

    def render(
            self,
            output_format=RENDER_FORMATS.text,
            add_summary=True,
            *args, **kwargs
    ):
        """Render report tree to the text.

        :param output_format: render format
                              text(default) json and yaml are supported.
        :type output_format: str|basestring

        :param add_summary: include statistics and result
        :type add_summary: bool

        :return: report strings
        :rtype: str|basestring
        """

        root_node = ReportNode(children=[self])
        if add_summary:
            summary_node = ReportNode(u'Summary:')
            fail_count = self.count_failures()
            if fail_count:
                summary_node.info(
                    u'Failure!')
                summary_node.info(
                    u'Please fix {} errors listed above.'.format(fail_count))
            else:
                summary_node.info(u'Success!')

            root_node.add_nodes(summary_node)

        return root_node._renderers[output_format](*args, **kwargs)

    def count_failures(self, start_from=0):
        """Count failure messages inside report.

        :param start_from: start count from
        :type start_from: int
        :return: errors count
        :rtype: int
        """
        count = start_from
        if self.failed:
            count += 1
        for child in self.children:
            count = child.count_failures(count)
        return count

    def is_failed(self):
        """Is this report about failure.

        :return: is failed
        :rtype: boolean
        """
        return bool(self.count_failures())

    def is_successful(self):
        """Is this report OK.

        :return: is successful
        :rtype: boolean
        """
        return not bool(self.count_failures())

    def mix_to_data(self, data):
        """Replace data with reported data with .report attribute

        :param data: list|dict
        :return: data with report
        :rtype: DataWithReport|ListResultWithReport|DictResultWithReport
        """
        if isinstance(data, list):
            return ListResultWithReport(data, self)
        else:
            return DictResultWithReport(data, self)
