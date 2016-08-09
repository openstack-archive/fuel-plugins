# -*- coding: utf-8 -*-
#
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

import jsonschema
import six
from yaml import YAMLError

from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.files_manager import files_manager
from fuel_plugin_builder.validators.report import ReportNode


# Basic rules of the Fight Club:
# 1. Check could call another check.
# 2. Check always returning Report node.
# 3. Name check's function starting from check_*.


def check_yaml_loadable(path):
    """Load yaml file and try to parse it.

    :param path: path of YAML file
    :type path: string
    :return: data or nothing
    :rtype: list|dict|None
    """
    report = ReportNode()
    try:
        return files_manager.load(path)
    except IOError as (errno, strerror):
        report.error("I/O error({0}): {1}".format(errno, strerror))
    except YAMLError as exc:
        error_message = "Can't parse YAML file"
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            error_message += ", error position: (%s:%s)" % (
                mark.line + 1, mark.column + 1)
            report.error(error_message)
    return report


def check_json_schema_is_valid(schema, data):
    """Check data with JSON Schema.

    :param schema: JSON Schema
    :type schema: list|dict
    :param data: data to check
    :type data: list|dict

    :return: report node
    :rtype: ReportNode
    """
    report_node = ReportNode()
    validator = jsonschema.Draft4Validator(schema)

    def _make_exceptions_report(json_schema_errors, report_node):
        """Make detailed report tree of JSON errors.

        :param json_schema_errors: validation errors
        :type json_schema_errors: iterable[ValidationError]
        :param report_node: report node
        :type report_node: ReportNode

        :return: report node
        :rtype: ReportNode
        """
        for exc in sorted(json_schema_errors, key=lambda e: e.path):
            path = ' -> '.join(
                map(six.text_type, exc.path)) or None
            sub_report_node = ReportNode(path)
            if exc.message:
                sub_report_node.error(exc.message)
            report_node.add_nodes(sub_report_node)
            if exc.context:  # make nested report nodes
                _make_exceptions_report(exc.context, sub_report_node)
        return report_node

    return _make_exceptions_report(validator.iter_errors(data), report_node)


def check_multi_json_schema_is_valid(schemas, data):
    """Checks multiple json schema based on record ``type`` field.

    :param schemas: dict of schemas in format
                        {
                            'type1': schema1,
                            'type2': schema2
                        }
    :type schemas: dict
    :param data: data tree
    :type data: dict[list|dict]

    :return: report
    :rtype ReportNode:
    """
    report = ReportNode()
    if not isinstance(data, list):
        report.error("Data should be a list of entities")
        return report
    for record_id, record in enumerate(data):
        record_type = record.get('type', '')
        schema = schemas.get(record_type)
        if schema is not None:
            report.add_nodes(
                check_json_schema_is_valid(schema, record)
            )
        else:
            report.error('Invalid type: {0} for record: {1}'.format(
                record_type, record_id
            ))
    return report


def check_path_exists(path):
    """Check if path is exists.

    :param path: path
    :type path: str

    :return: report
    :rtype ReportNode:
    """
    report = ReportNode()

    if utils.paths.is_exists(path):
        report.error("Path not exists")
    return report


def check_dir_exists(path):
    """Check if dir is exists.

    :param path: path
    :type path: str

    :return: report
    :rtype ReportNode:
    """
    report = ReportNode(text=path)

    if not utils.paths.is_dir(path):
        report.error('Directory not exists')
    return report


def check_file_exists(path):
    """Check if file is exists.

    :param path: path
    :type path: str

    :return: report
    :rtype ReportNode:
    """
    result = ReportNode(text=path)

    if not utils.fs.is_exists(path):
        result.error('File not found')
    return result


def check_release_compatible(basic_version, plugin_metadata):
    """Checks version compatibility.

    :param basic_version: basic supported version
    :type basic_version: str
    :param plugin_metadata: plugin metadata root
    :type plugin_metadata: dict

    :return: report
    :rtype ReportNode:
    """
    result = ReportNode(u'Checking version compatibility')
    result.info(u'Expected Fuel version >= {0}'.format(basic_version))
    incompatible_versions = list()
    compatible_versions = list()

    for fuel_version in plugin_metadata.get('fuel_version', []):
        if (
            utils.strict_version(fuel_version) <
            utils.strict_version(basic_version)
        ):
            incompatible_versions.append(fuel_version)
        else:
            compatible_versions.append(fuel_version)

    if not compatible_versions:
        result.error(
            u'Current plugin format {0} is not compatible with following Fuel '
            u'versions: {2}\n'
            u'Fuel version must be {1} or higher. '
            u'Please remove {2} version from metadata.yaml file or '
            u'downgrade package_version.'
            .format(
                plugin_metadata['package_version'],
                basic_version,
                ', '.join(incompatible_versions)))

    if compatible_versions:
        if incompatible_versions:
            result.warning(
                u'Current plugin format {0} is not compatible with following '
                u'Fuel versions: {2}\n'
                u'Fuel version must be {1} or higher. '
                u'Please remove {2} version from metadata.yaml file or '
                u'downgrade package_version.'.format(
                    plugin_metadata['package_version'],
                    basic_version,
                    ', '.join(incompatible_versions)))

        result.info(u'Check done!')

    return result
#
#
# def check_fuel_compatible(minimal_fuel_version, plugin_metadata):
#     """Checks version compatibility.
#
#     :param minimal_fuel_version: basic supported version
#     :type minimal_fuel_version: str
#     :param plugin_metadata: plugin metadata root
#     :type plugin_metadata: dict
#
#     :return: report
#     :rtype ReportNode:
#     """
#     report = ReportNode(u'Checking version compatibility')
#     report.info(u'Expected Fuel version >= {0}'.format(minimal_fuel_version))
#
#     compatible_version_found = False
#
#     for metadata_fuel_version in plugin_metadata.get('fuel_version', []):
#         if (
#             utils.strict_version(metadata_fuel_version) <
#             utils.strict_version(minimal_fuel_version)
#         ):
#             report.warning(
#                 u'Current plugin package format {package_version} is not '
#                 u'compatible with {metadata_fuel_version} Fuel version. '
#                 u'Fuel version must be {minimal_fuel_version} or higher. '
#                 u'Please remove {metadata_fuel_version} version from '
#                 u'{metadata_path} file or downgrade package_version.'
#                 .format(
#                     package_version=plugin_metadata['package_version'],
#                     minimal_fuel_version=minimal_fuel_version,
#                     metadata_fuel_version=metadata_fuel_version,
#                     metadata_path='metadata.yaml'
#                 ))
#         else:
#             report.info(u"Compatible version found: {}"
#                         u"".format(metadata_fuel_version))
#             compatible_version_found = True
#
#     if not compatible_version_found:
#         report.error(u'No compatible versions found')
#     return report
