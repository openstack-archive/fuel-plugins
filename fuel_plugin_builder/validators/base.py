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

import abc
from distutils.version import StrictVersion
import logging
import os
import sys

import collections
import jsonschema
import six

from fuel_plugin_builder import errors
from fuel_plugin_builder import utils

# There is two base validators:
#
# LegacyBaseValidator is used for v1 - v3 plugin package version validation.
#
# New BaseValidator targeted to plugin package version v4=< is using
# Inspections/Checks to describe custom logic and providing based on
# ReportNode class.
#
# Check is a basic logic unit that performing validations with
# 1. path
# 2. all files in given path
# and returning ReportNode that contain all messages and errors.
#
# Inspection is sequentially running group of Checks against given path and
# also returning ReportNode.
#
# You are free to use nested checks and inspections inside checks.
#
# Validator (BaseValidator) is running inspections from the inspections
# property that is supposed to be main and only customisation area.
#
# Its not recommended to inherit Validators other than BaseValidator from each
# other creating multiple levels of inheritance because it makes hard to trace,
# test and debug where and what checks is applied.

# size of the new level text indent when rendering report
REPORT_INDENT_SIZE = 4
# symbol to mark error nodes when rendering report
REPORT_FAILURE_POINTER = '> '

logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class LegacyBaseValidator(object):
    """This class is deprecated, please, use
    """
    @abc.abstractproperty
    def basic_version(self):
        pass

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path

    def validate_schema(self, data, schema, file_path, value_path=None):
        logger.debug(
            'Start schema validation for %s file, %s', file_path, schema)

        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as exc:
            raise errors.ValidationError(
                self._make_error_message(exc, file_path, value_path))

    def _make_error_message(self, exc, file_path, value_path):
        if value_path is None:
            value_path = []

        if exc.absolute_path:
            value_path.extend(exc.absolute_path)

        if exc.context:
            sub_exceptions = sorted(
                exc.context, key=lambda e: len(e.schema_path), reverse=True)
            sub_message = sub_exceptions[0]
            value_path.extend(list(sub_message.absolute_path)[2:])
            message = sub_message.message
        else:
            message = exc.message

        error_msg = "File '{0}', {1}".format(file_path, message)

        if value_path:
            value_path = ' -> '.join(map(six.text_type, value_path))
            error_msg = '{0}, {1}'.format(
                error_msg, "value path '{0}'".format(value_path))

        return error_msg

    def validate_file_by_schema(self, schema, file_path,
                                allow_not_exists=False, allow_empty=False):
        """Validate file with given JSON schema.

        :param schema: object dict
        :type schema: object
        :param file_path: path to the file
        :type file_path: basestring
        :param allow_not_exists: if true don't raise error on missing file
        :type allow_not_exists: bool
        :param allow_empty: allow file to contain no json
        :type allow_empty: bool
        :return:
        """
        if not utils.exists(file_path):
            if allow_not_exists:
                logger.debug('No file "%s". Skipping check.', file_path)
                return
            else:
                raise errors.FileDoesNotExist(file_path)

        data = utils.parse_yaml(file_path)
        if data is not None:
            self.validate_schema(data, schema, file_path)
        else:
            if not allow_empty:
                raise errors.FileIsEmpty(file_path)

    @abc.abstractmethod
    def validate(self):
        """Performs validation
        """

    def check_schemas(self):
        logger.debug('Start schema checking "%s"', self.plugin_path)
        self.validate_file_by_schema(
            self.schema.metadata_schema,
            self.meta_path)
        self.validate_file_by_schema(
            self.schema.tasks_schema,
            self.tasks_path)
        self.check_env_config_attrs()

    def check_env_config_attrs(self):
        """Check attributes in environment config file.

        'attributes' is not required field, but if it's
        present it should contain UI elements OR metadata
        structure.
        """
        config = utils.parse_yaml(self.env_conf_path)
        if not config:
            return

        self.validate_schema(
            config,
            self.schema.attr_root_schema,
            self.env_conf_path)

        attrs = config.get('attributes', {})
        for attr_id, attr in six.iteritems(attrs):
            schema = self.schema.attr_element_schema
            # Metadata object is totally different
            # from the others, we have to set different
            # validator for it
            if attr_id == 'metadata':
                schema = self.schema.attr_meta_schema

            self.validate_schema(
                attr,
                schema,
                self.env_conf_path,
                value_path=['attributes', attr_id])

    def check_releases_paths(self):
        meta = utils.parse_yaml(self.meta_path)
        for release in meta['releases']:
            scripts_path = os.path.join(
                self.plugin_path,
                release['deployment_scripts_path'])
            repo_path = os.path.join(
                self.plugin_path,
                release['repository_path'])

            wrong_paths = []
            for path in [scripts_path, repo_path]:
                if not utils.exists(path):
                    wrong_paths.append(path)

            if wrong_paths:
                raise errors.ReleasesDirectoriesError(
                    'Cannot find directories {0} for release "{1}"'.format(
                        ', '.join(wrong_paths), release))

    def check_compatibility(self):
        """Json schema doesn't have any conditions, so we have
        to make sure here, that this validation schema can be used
        for described fuel releases
        """
        meta = utils.parse_yaml(self.meta_path)
        for fuel_release in meta['fuel_version']:
            if StrictVersion(fuel_release) < StrictVersion(self.basic_version):
                raise errors.ValidationError(
                    'Current plugin format {0} is not compatible with {2} Fuel'
                    ' release. Fuel version must be {1} or higher.'
                    ' Please remove {2} version from metadata.yaml file or'
                    ' downgrade package_version.'
                    .format(
                        meta['package_version'],
                        self.basic_version,
                        fuel_release))


@six.add_metaclass(abc.ABCMeta)
class BaseValidator(object):
    """New style validator based on Check/Inspection/ReportNode entities."""
    def __init__(self, plugin_path):
        """Initialize.

        :param plugin_path: plugin path
        :type plugin_path: basestring
        """
        self.plugin_path = plugin_path

    @abc.abstractproperty
    def inspections(self):
        """List of Inspection.

        :return: list of inspections
        :rtype: list[Inspection]
        """
        return []

    def _get_plugin_path(self, path='.'):
        return os.path.join(self.plugin_path, path)

    def validate(self):
        """Perform validation and write result to the stdout."""

        # create root ReportNode and place all inspections results under it
        report = ReportNode('Validating: {0}'.format(self.plugin_path))

        for inspection in self.inspections:
            report.add_nodes(inspection.check())

        sys.stdout.write(report.render())
        failures_count = report.count_failures()

        if failures_count:
            msg = '\n'.join([
                '',
                'VALIDATION FAILED!',
                'Please fix {0} errors listed above.'.format(failures_count)])
            sys.stdout.write(msg)
            # sys.stderr.write(msg)
        else:
            sys.stdout.write('\n\nValidation successful!')

        return not failures_count


class Inspection(object):
    def __init__(self, checks, name="", path="."):
        """Create inspection that is running named set of checks against given
        path.

        :param checks: list of checks that will run sequentially.
        :type checks: list[Check]
        :param name: inspection name that will be used in report.
        :type name: basestring
        :param path: path
        :type path: basestring
        """
        if checks:
            self.checks = checks
        else:
            raise errors.CheckConfigurationError("No checks provided")
        self.name = name
        self.path = path

    def check(self):
        """Check inspection paths.
        For each path Check.check_path of Check is applied to the whole path
        then all Check.check_file is applied to each of file found at
        given path.
        """
        if not self.checks:
            raise errors.CheckConfigurationError("No checks defined")

        # combine all check reports by path
        reports_by_path = collections.defaultdict(list)

        for check in self.checks:
            # check path
            check_result = check.check_path(self.path)
            if not isinstance(check_result, ReportNode):
                raise errors.CheckConfigurationError(
                    "Check {0} returned non-report value "
                    "{1}".format(check, check_result))
            reports_by_path[self.path].append(check_result)

            # check every file in path
            for file_path in utils.files_in_path(self.path):
                check_result = check.check_file(file_path)
                if not isinstance(check_result, ReportNode):
                    raise errors.CheckConfigurationError(
                        "Check {0} returned non-report value "
                        "{1}".format(check, check_result))
                reports_by_path[self.path].append(check_result)

        # merge result to report tree grouping by paths
        inspection_report = ReportNode(text="Inspection: " + self.name)
        for path, path_reports in six.iteritems(reports_by_path):
            path_report_node = ReportNode(self.path)
            path_report_node.add_nodes(path_reports)
            inspection_report.add_nodes(path_report_node)

        return inspection_report


class ReportNode(object):

    def __init__(self, text=None, children=None, failed=False):
        """Create basic unit of report tree.
        There is no Report class because i'ts redundant and
        any root ReportNode could be considered as report.

        :param text: node text
        :type text: basestring
        :param children: list of child ReportNodes
        :type children: list[ReportNode]
        :param failed: failure flag that affects rendering
        :type failed: boolean
        """
        self.text = text
        self.children = children or []
        self.failed = failed

    def add_nodes(self, nodes):
        """Add single node or several nodes.

        :param nodes: one or several report nodes
        :type nodes: list|tuple|ReportNode
        """
        # single node
        if isinstance(nodes, ReportNode):
            self.children.append(nodes)
        else:
            self.children.extend(
                node for node in nodes if isinstance(node, ReportNode)
            )

    def error(self, msg):
        """Add error message to output.

        :param msg: text
        :type msg: basestring
        """
        self.add_nodes(ReportNode('ERROR: ' + msg, failed=True))

    def warning(self, msg):
        """Add warning message to output.

        :param msg: text
        :type msg: basestring
        """
        self.add_nodes(ReportNode('WARNING: ' + msg, failed=False))

    def info(self, msg):
        """Add info message to output.

        :param msg: text
        :type msg: basestring
        """
        self.add_nodes(ReportNode('INFO: ' + msg, failed=False))

    def _render(self, level=0):
        """Render report tree to the validation result and messages list.

        :param level: indent level
        :type level: int
        :return: failed flag and list of message strings
        :rtype: (list[str], bool)
        """
        indent = REPORT_INDENT_SIZE * level
        error_indent = max(indent - len(REPORT_FAILURE_POINTER), 0)

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
                (error_indent if failed else indent) * ' ',
                REPORT_FAILURE_POINTER if failed else '',
                self.text
            ])
            strings.insert(0, output)
        return strings, failed

    def render(self):
        """Render report tree to the text."""
        strings, _ = self._render()
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


class Check(object):

    def check_path(self, path):
        """Check of any path, use for all common path checks like naming,
        files/folders structure e.t.c.

        :param path: path to file or folder
        :type path: basestring
        :returns: result
        :rtype: fuel_plugin_builder.validators.base.CheckResult
        """
        return ReportNode()

    def check_file(self, path):
        """Check file with given path.

        :param path: path to file
        :type path: basestring
        :returns: result
        :rtype: fuel_plugin_builder.validators.base.CheckResult
        """
        return ReportNode()
