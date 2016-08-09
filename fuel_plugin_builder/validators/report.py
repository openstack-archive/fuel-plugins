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

from fuel_plugin_builder import consts
from fuel_plugin_builder import errors


class ReportNode(object):
    """Basic unit of Reports tree.

    Any ReportNode could be rendered as report with all children tree.
    """

    text = None
    children = None
    failed = False

    def __init__(self, text=None, children=None, failed=False):
        """Basic unit of report tree.

        :param text: node text
        :type text: str
        :param children: list of child ReportNodes
        :type children: list[ReportNode]
        :param failed: failure flag that affects rendering
        :type failed: boolean
        """
        self.text = text
        self.children = children if children is not None else []
        self.failed = failed

    def _render(self, level=0):
        """Render report tree to the validation result and messages list.

        :param level: indent level
        :type level: int
        :return: failed flag and list of message strings
        :rtype: (list[str], bool)
        """
        indent_size = consts.REPORT_INDENT_SIZE * level
        error_indent_size = \
            max(indent_size - len(consts.REPORT_FAILURE_POINTER), 0)
        indent = indent_size * ' '
        error_indent = error_indent_size * ' '

        strings = []
        failed = self.failed
        # no indent is required if we have no output on this level
        next_level = level + (1 if self.text else 0)
        for child in self.children:
            child_strings, child_failed = child._render(next_level)
            failed = child_failed or failed
            strings.extend(child_strings)

        if self.text:
            output = ''.join([
                error_indent if failed else indent,
                consts.REPORT_FAILURE_POINTER if failed else '',
                self.text
            ])
            strings.insert(0, output)
        return strings, failed

    @property
    def ok(self):
        return self.count_failures() == 0

    @property
    def failed(self):
        return self.count_failures() > 0

    def add_nodes(self, *nodes):
        """Add single node or several nodes.

        :param nodes: one or several report nodes
        :type nodes: list[ReportNode]
        :raises: InspectionConfigurationError
        """
        for node in nodes:
            if not isinstance(node, ReportNode):
                raise errors.InspectionConfigurationError(
                    "This value is not ReportNode {0}".format(node))
            self.children.append(node)
        return self

    def error(self, msg, fail=True):
        """Add child ReportNode with error message.

        :param msg: text
        :type msg: str
        :param fail: set node as failed
        :type fail: bool
        """
        if fail:
            self.failed = True
        return self.add_nodes(ReportNode('ERROR: ' + msg, failed=True))

    def warning(self, msg):
        """Add child ReportNode with warning message.

        :param msg: text
        :type msg: str
        """
        return self.add_nodes(ReportNode('WARNING: ' + msg, failed=False))

    def info(self, msg):
        """Add child ReportNode with info message.

        :param msg: text
        :type msg: str
        """
        return self.add_nodes(ReportNode('INFO: ' + msg, failed=False))

    def render(self, add_summary=True):
        """Render report tree to the text.

        :param add_summary: include statistics and result
        :type add_summary: bool

        :return: report strings
        :rtype: str
        """
        strings, _ = self._render()

        if add_summary:
            strings.append('')
            failures_count = self.count_failures()
            if failures_count:
                strings += [
                    'VALIDATION FAILED!',
                    'Please fix {0} errors listed above.'.format(
                        failures_count)
                ]
            else:
                strings += [
                    'Validation successful!'
                ]

        return "\n".join(strings)

    def count_failures(self, start_from=0):
        """Count failures.

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
