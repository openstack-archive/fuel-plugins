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

from distutils import version
import os

import jsonschema
import six
from yaml import YAMLError

from fuel_plugin_builder import utils
from fuel_plugin_builder.validators.base import BaseCheck
from fuel_plugin_builder.validators.base import ReportNode

from schemas.base import BaseSchema

# This file contains checks which are used by validators


class YamlLoadMixin(object):
    """Provide method to load YAML file and parse it."""
    @staticmethod
    def _load_yaml(path, report_node):
        """Load yaml file and parse it.

        :param path: path of YAML file
        :type path: basestring
        :param report_node: report node
        :type report_node: ReportNode
        :return: data or nothing
        :rtype: list|dict|None
        """
        try:
            return utils.parse_yaml(path)
        except IOError as (errno, strerror):
            report_node.error("I/O error({0}): {1}".format(errno, strerror))
        except YAMLError as exc:
            error_message = "Can't parse YAML file"
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                error_message += ", error position: (%s:%s)" % (
                    mark.line + 1, mark.column + 1)
            report_node.error(error_message)


class JSONSchemaCheckMixin(object):
    """Provides method to check JSON Schema data."""
    @staticmethod
    def _check_json_schema(schema, data, report_node):
        """Check data with JSON Schema.

        :param schema: JSON Schema
        :type schema: list|dict
        :param data: data to check
        :type data: list|dict
        :param report_node: report node
        :type report_node: ReportNode
        :return: report node
        :rtype: ReportNode
        """
        validator = jsonschema.Draft4Validator(schema)

        def make_exceptions_report(exceptions, report_node):
            for exc in sorted(exceptions, key=lambda e: e.path):
                path = ' -> '.join(
                    map(six.text_type, exc.path)) or None
                sub_report_node = ReportNode(path)
                if exc.message:
                    sub_report_node.error(exc.message)
                report_node.add_nodes(sub_report_node)
                if exc.context:  # make nested report nodes
                    make_exceptions_report(exc.context, sub_report_node)
            return report_node

        make_exceptions_report(validator.iter_errors(data), report_node)
        return report_node


class JSONSchemaIsValid(BaseCheck, YamlLoadMixin, JSONSchemaCheckMixin):
    """Checks if file JSON Schema is valid."""
    def __init__(self, schema):
        """Initialise.

        :param schema: JSON Schema
        :type schema: dict[list|dict]
        """
        super(JSONSchemaIsValid, self).__init__()
        self.schema = schema

    def check_file(self, path):
        result = super(JSONSchemaIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        self._check_json_schema(self.schema, data, result)
        return result


class MultiJSONSchemaIsValid(BaseCheck, YamlLoadMixin, JSONSchemaCheckMixin):
    """Checks multiple json schema based on record ``type`` field."""
    def __init__(self, schemas):
        """Initialise.

        :param schemas: dict of schemas in format
                            {
                                'type1': schema1,
                                'type2': schema2
                            }
        :type schemas: dict
        """
        super(MultiJSONSchemaIsValid, self).__init__()
        self.schemas = schemas

    def check_file(self, path):
        result = super(MultiJSONSchemaIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        if not isinstance(data, list):
            result.error("Data should be a list of entities")
            return result
        for record_id, record in enumerate(data):
            record_type = record.get('type', '')
            schema = self.schemas.get(record_type)
            if schema is not None:
                self._check_json_schema(schema, record, result)
            else:
                result.error('Invalid type: {0} for record: {1}'.format(
                    record_type, record_id
                ))
        return result


class DoPathHaveFiles(BaseCheck):
    """Checks if there are files in path."""
    def __init__(self, required=True):
        """Initialise.

        :param required: is file existence required
        :type required: bool
        """
        super(DoPathHaveFiles, self).__init__()
        self.required = required

    def check_path(self, path):
        result = super(DoPathHaveFiles, self).check_path(path)
        if not utils.files_in_path(path):
            result.error('Path contain no files')
        return result


class IsFile(BaseCheck):
    """Checks return if given path is file."""
    def __init__(self, required=True):
        """Initialise.

        :param required: is file existence required
        :type required: bool
        """
        super(IsFile, self).__init__()
        self.required = required

    def check_path(self, path):
        result = super(IsFile, self).check_path(path)
        if utils.exists(path):
            if not utils.isfile(path):
                result.error('Path is not file')
        else:
            if self.required:
                result.error('File not found')
        return result


class IsReleaseCompatible(BaseCheck, YamlLoadMixin):
    """Checks version compatibility."""
    def __init__(self, basic_version):
        """Initialise.

        :param basic_version: basic supported version
        :type basic_version: basestring
        """
        super(IsReleaseCompatible, self).__init__()
        self.basic_version = basic_version

    def check_file(self, path):
        result = super(IsReleaseCompatible, self).check_file(path)
        result.info('Expected Fuel version >={0}'.format(self.basic_version))
        data = self._load_yaml(path, result)
        for fuel_release in data['fuel_version']:
            if (
                version.StrictVersion(fuel_release) <
                version.StrictVersion(self.basic_version)
            ):
                result.error(
                    'Current plugin format {0} is not compatible with {2} Fuel'
                    ' release. Fuel version must be {1} or higher.'
                    ' Please remove {2} version from metadata.yaml file or'
                    ' downgrade package_version.'
                    .format(
                        data['package_version'],
                        self.basic_version,
                        fuel_release))
        return result


class ScriptsAndRepoPathsIsValid(BaseCheck, YamlLoadMixin):
    """Checks releases paths correctness."""
    def __init__(self, base_path):
        """Initialise.

        :param base_path: base path
        :type base_path: basestring
        """
        super(ScriptsAndRepoPathsIsValid, self).__init__()
        self.base_path = base_path

    RELEASE_PATHS = ['deployment_scripts_path', 'repository_path']

    def check_file(self, path):
        result = super(ScriptsAndRepoPathsIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        for release in data['releases']:
            for path_field in self.RELEASE_PATHS:
                release_path = release.get(path_field)
                if release_path is None:
                    result.error('Field {0} not specified for the release '
                                 '{1}'.format(path_field, release))
                    continue
                path_to_check = os.path.join(self.base_path, release_path)
                if not utils.exists(path_to_check):
                    result.error(
                        'Cannot find directory {0} for the release '
                        '"{1}"'.format(path_to_check, release))
        return result


class EnvConfigAttrsIsValidV1(BaseCheck, YamlLoadMixin, JSONSchemaCheckMixin):
    """Checks environment config attributes."""
    def check_file(self, path):
        base_schema = BaseSchema()
        result = super(EnvConfigAttrsIsValidV1, self).check_file(path)
        data = self._load_yaml(path, result)
        self._check_json_schema(base_schema.attr_root_schema, data, result)
        attributes = data.get('attributes', {}) or {}
        for attr_id, attr in six.iteritems(attributes):
            # Metadata object is totally different
            # from the others, we have to set different
            # validator for it
            if attr_id == 'metadata':
                schema = base_schema.attr_meta_schema
            else:
                schema = base_schema.attr_element_schema
            schema_report = ReportNode('attributes -> {0}'.format(attr_id))
            self._check_json_schema(schema, attr, schema_report)
            result.add_nodes(schema_report)
        return result
