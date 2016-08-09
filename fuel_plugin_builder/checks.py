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

import utils


# This file provides number of functions which making some plugin-specific data
# requirements/integrity and file system checks and returning report.
#
# Basic rules of using checks:
# 1. Check wrapped with @check decorator providing clear report node.
# 2. Check could call another check and use it's report.
# 3. Check always returning a Report node.


def check(f):
    """Check decorator.

    :param f: function
    :type f: function

    :return: decorated function
    :rtype: function
    """

    def func_wrapper(*args, **kwargs):
        report = utils.ReportNode()
        result = f(report, *args, **kwargs)
        assert isinstance(result, utils.ReportNode)
        return result

    return func_wrapper


@check
def json_schema_is_valid(report, schema, data):
    """Check data with JSON Schema.

    :param report: report node
    :type report: ReportNode
    :param schema: JSON Schema
    :type schema: list|dict
    :param data: data to check
    :type data: list|dict

    :return: report node
    :rtype: utils.ReportNode
    """

    report.info(u"Checking JSON schema")
    json_schema_validator = jsonschema.Draft4Validator(schema)

    def _convert_errors_tree_report_tree(json_schema_errors, report_node):
        """Make detailed report tree of JSON errors.

        :param json_schema_errors: validation errors
        :type json_schema_errors: iterable[ValidationError]
        :param report_node: report node
        :type report_node: ReportNode

        :return: report node
        :rtype: utils.ReportNode
        """
        for exc in sorted(json_schema_errors, key=lambda e: e.path):
            path = u' -> '.join(
                map(six.text_type, exc.path)) or None
            sub_report_node = utils.ReportNode(path)
            if exc.message:
                sub_report_node.error(exc.message)
            report_node.add_nodes(sub_report_node)
            if exc.context:  # make nested report nodes
                _convert_errors_tree_report_tree(
                    exc.context,
                    sub_report_node
                )
        return report_node

    child_report = utils.ReportNode(' ')

    _convert_errors_tree_report_tree(
        json_schema_validator.iter_errors(data),
        child_report
    )
    report.add_nodes(child_report)
    return report


@check
def multi_json_schema_is_valid(report, schemas, data):
    """Checks multiple JSON Schema using record ``type`` field to choose
    appropriate schema.

    :param report: report node
    :type report: ReportNode
    :param schemas: dict of schemas in format
                        {
                            'type1': schema1,
                            'type2': schema2
                        }
    :type schemas: dict
    :param data: data tree
    :type data: list[list|dict]

    :return: report
    :rtype: utils.ReportNode
    """
    report.info(u"Checking multi JSON schema is valid")
    if not isinstance(data, list):
        report.error(u'Data should be a list of entities')
        return report
    for record_id, record in enumerate(data):
        record_type = record.get('type', '')
        schema = schemas.get(record_type)
        if schema is not None:
            report.add_nodes(
                json_schema_is_valid(schema, record)
            )
        else:
            report.error(u'Invalid type: {0} for record: {1}'.format(
                record_type, record_id
            ))
    return report


@check
def path_exists(report, path):
    """Check if path is exists or path mask has been resolved to at least
    one path.

    :param report: report node
    :type report: ReportNode
    :param path: path
    :type path: basestring|str

    :return: report
    :rtype: utils.ReportNode
    """
    report.info(u'Checking path existence: {}'.format(path))

    if not utils.fs.get_paths(path):
        report.error(u'Path not exists')

    return report


@check
def dir_exists(report, path):
    """Check if dir is exists.

    :param report: report node
    :type report: ReportNode
    :param path: path
    :type path: str

    :return: report
    :rtype: utils.ReportNode
    """
    report.info(path)

    if not utils.fs.is_dir(path):
        report.error(u'Directory not exists')
    return report


@check
def file_exists(report, path):
    """Check if file is exists.

    :param report: report node
    :type report: ReportNode
    :param path: path
    :type path: str

    :return: report
    :rtype: utils.ReportNode
    """
    report.info(path)

    if not (utils.fs.is_exists(path) and utils.fs.is_file(path)):
        report.error(u'File not found')
    return report


@check
def fuel_ver_compatible_with_package_ver(
        report, minimal_fuel_version, plugin_metadata):
    """Checks Fuel version compatibility with plugin package version.

    :param report: report node
    :type report: ReportNode
    :param minimal_fuel_version: basic supported version
    :type minimal_fuel_version: str
    :param plugin_metadata: plugin metadata root
    :type plugin_metadata: dict

    :return: report
    :rtype: utils.ReportNode
    """
    report.info(u'Checking version compatibility')
    report.info(u'Expected Fuel version >= {0}'.format(minimal_fuel_version))
    incompatible_versions = list()

    for fuel_version in plugin_metadata.get('fuel_version', []):
        if (
            utils.strict_version(fuel_version) <
            utils.strict_version(minimal_fuel_version)
        ):
            incompatible_versions.append(fuel_version)

    if incompatible_versions:
        report.error(
            u'Current plugin format {0} is not compatible with following Fuel '
            u'versions: {2}\n'
            u'Fuel version must be {1} or higher. '
            u'Please remove {2} version from metadata.yaml file or '
            u'downgrade package_version.'
            .format(
                plugin_metadata['package_version'],
                minimal_fuel_version,
                ', '.join(incompatible_versions)
            )
        )
    else:
        report.info(u'Plugin is compatible with target Fuel version.')

    return report


@check
def legacy_fuel_version(report, metadata):
    if metadata.get('fuel_version'):
        report.warning(u'"fuel_version" field in metadata.yaml is deprecated '
                       u'and will be removed in further Fuel releases.')
    return report


@check
def env_attributes(report, data, attr_root_schema,
                   attribute_schema, attribute_meta_schema):
    """Check attributes in environment config file.
    'attributes' is not required field, but if it's
    present it should contain UI elements OR metadata
    structure.

    :param report: report node
    :type report: ReportNode
    :param data: attributes data
    :type data: dict
    :param attr_root_schema: dict
    :type attr_root_schema: JSON schema of attributes root
    :param attribute_schema: dict
    :type attribute_schema: JSON schema of attribute
    :param attribute_meta_schema: dict
    :type attribute_meta_schema: JSON schema of attribute

    :return: report
    :rtype: utils.ReportNode
    """

    print "DDD", data, attr_root_schema
    report.info(u"Checking environment attributes")
    report.add_nodes(
        json_schema_is_valid(attr_root_schema, data)
    )
    if report.is_failed():
        return report
    attrs = data.get('attributes', {}) or {}
    for attr_id, attr in six.iteritems(attrs):
        # Metadata object is totally different
        # from the others, we have to set different
        # validator for it
        if attr_id == 'metadata':
            schema = attribute_meta_schema
        else:
            schema = attribute_schema
        report.add_nodes(
            json_schema_is_valid(schema, attr)
        )
    return report


@check
def mode_directive(report, release_record):
    mode = release_record.get('mode')
    if mode is not None:
        report.warning(u'"mode" directive id deprecated and ignored by Fuel '
                       u'releases elder then 6.1')
    return report
