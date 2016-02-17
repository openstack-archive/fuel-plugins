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
from fuel_plugin_builder.validators.base import Check


class YamlCheckMixin(object):

    @staticmethod
    def _load_yaml(path, report_node):
        try:
            data = utils.parse_yaml_file(path)
            return data
        except IOError as (errno, strerror):
            report_node.error("I/O error({0}): {1}".format(errno, strerror))
        except YAMLError as exc:
            error_message = "Can't parse YAML file"
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                error_message += ", error position: (%s:%s)" % (
                    mark.line + 1, mark.column + 1)
            report_node.error(error_message)


# This file contains checks that is used by validators

class JsonSchemaIsValid(Check, YamlCheckMixin):
    def __init__(self, schema):
        """Check file JSON Schema.

        :param schema: JSON Schema
        :type schema: object
        """
        super(JsonSchemaIsValid, self).__init__()
        self.schema = schema

    def check_file(self, path):
        result = super(JsonSchemaIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.exceptions.ValidationError as exc:
            result.error(
                "JSON Schema validation failed, {0}".format(
                    utils.format_json_schema_error(exc)
                )
            )
        return result


class MultiJsonSchemaIsValid(Check, YamlCheckMixin):
    def __init__(self, schemas):
        """Check multiple json schema based on record `type` field.

        :param schemas: list of schemas in format
                            {
                                'type1': schema1,
                                'type2': schema2
                            }
        :type schemas: List[dict]
        """
        super(MultiJsonSchemaIsValid, self).__init__()
        self.schemas = schemas or {}

    def _check_records(self, data, result):
        for record_id, record in enumerate(data):
            task_type = record.get('type', '')
            schema = self.schemas.get(task_type)
            if schema is not None:
                try:
                    jsonschema.validate(record, schema)
                except jsonschema.exceptions.ValidationError as exc:
                    result.error(
                        "JSON Schema validation failed {0}".format(
                            utils.format_json_schema_error(exc)
                        )
                    )
            else:
                result.error('invalid task_type: {0} for record: {1}'.format(
                    task_type, record_id
                ))

    def check_file(self, path):
        result = super(MultiJsonSchemaIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        self._check_records(data, result)
        return result


class HaveDataFiles(Check):
    def __init__(self, required=True):
        """Check if there is some files in path.

        :param required: is file existence required
        :type required: bool
        """
        super(HaveDataFiles, self).__init__()
        self.required = required

    def check_path(self, path):
        result = super(HaveDataFiles, self).check_path(path)
        if not utils.exists(path):
            result.error('Path does not exist')
        elif not utils.files_in_path(path):
            result.error('Path is empty directory')
        return result


class IsFile(Check):
    def __init__(self, required=True):
        """Check return if given path is file.

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


class IsCompatible(Check, YamlCheckMixin):
    def __init__(self, basic_version):
        """Check version compatibility

        :param basic_version: basic supported version
        :type basic_version: basestring
        """
        super(IsCompatible, self).__init__()
        self.basic_version = basic_version

    def check_file(self, path):
        result = super(IsCompatible, self).check_file(path)
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


class ReleasesPathsIsValid(Check, YamlCheckMixin):

    def __init__(self, base_path):
        """Check releases paths.

        :param base_path: base path
        :type base_path: basestring
        """
        super(ReleasesPathsIsValid, self).__init__()
        self.base_path = base_path

    def check_file(self, path):
        result = super(ReleasesPathsIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        for release in data['releases']:
            scripts_path = os.path.join(
                self.base_path,
                release['deployment_scripts_path'])
            repo_path = os.path.join(
                self.base_path,
                release['repository_path'])
            wrong_paths = []
            for path in [scripts_path, repo_path]:
                if not utils.exists(os.path.join(self.base_path, path)):
                    wrong_paths.append(path)
            if wrong_paths:
                result.error(
                    'Cannot find directories {0} for release "{1}"'.format(
                        ', '.join(wrong_paths), release))
        return result


class EnvConfigAttrsIsValid(Check, YamlCheckMixin):

    def __init__(self,
                 attr_root_schema, attr_element_schema, attr_meta_schema):
        """Check environment config attributes.

        :param attr_root_schema: attributes root schema
        :type attr_root_schema: object
        :param attr_element_schema: attributes element schema
        :type attr_element_schema: object
        :param attr_meta_schema: attributes metadata schema
        :type attr_meta_schema: object
        """
        super(EnvConfigAttrsIsValid, self).__init__()
        self._attr_element_schema = attr_element_schema
        self._attr_meta_schema = attr_meta_schema
        self._attr_root_schema = attr_root_schema

    def check_file(self, path):
        result = super(EnvConfigAttrsIsValid, self).check_file(path)
        data = self._load_yaml(path, result)
        try:
            jsonschema.validate(data, self._attr_root_schema)
        except jsonschema.exceptions.ValidationError as exc:
            result.error(
                "JSON Schema validation failed {0}".format(
                    utils.format_json_schema_error(exc)
                )
            )

        attributes = data.get('attributes', {})

        for attr_id, attr in six.iteritems(attributes):
            # Metadata object is totally different
            # from the others, we have to set different
            # validator for it
            if attr_id == 'metadata':
                schema = self._attr_meta_schema
            else:
                schema = self._attr_element_schema

            try:
                jsonschema.validate(attr, schema)
            except jsonschema.exceptions.ValidationError as exc:
                result.error(
                    "JSON Schema validation failed {0}".format(
                        utils.format_json_schema_error(exc)
                    )
                )
        return result
