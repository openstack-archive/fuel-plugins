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


def get_plugin_for_version(version):
    """Retrieves data which are required for specific version of plugin

        :param str version: version of package
        :returns: dict which contains
                  'version' - package version
                  'templates' - array of paths to templates
                  'validator' - validator class
                  'builder' - builder class
        """
    from fuel_plugin_builder import errors
    from fuel_plugin_builder import validators
    from fuel_plugin_builder import loaders
    from fuel_plugin_builder import builders
    mapping = {
        '5.0.0': {
            'version': '5.0.0',
            'templates': [
                'templates/base',
                'templates/v5/plugin_data/'
            ],

            'loader': loaders.loader_v5.LoaderV5,
            'validator': validators.validator_v5.ValidatorV5,
            'builder': builders.BuildPluginV3  # build process have not
                                               # changed
        },
        '4.0.0': {
            'version': '4.0.0',
            'templates': [
                'templates/base',
                'templates/v3/plugin_data/',
                'templates/v4/plugin_data/'
            ],
            'loader': loaders.loader_v4.LoaderV4,
            'validator': validators.validator_v4.ValidatorV4,
            'builder': builders.BuildPluginV3   # build process have not
                                                # changed
        },
        '3.0.0': {
            'version': '3.0.0',
            'templates': [
                'templates/base',
                'templates/v3/plugin_data/'
            ],

            'loader': loaders.loader_v3.LoaderV3,
            'validator': validators.validator_v3.ValidatorV3,
            'builder': builders.BuildPluginV3
        },
        '2.0.0': {
            'version': '2.0.0',
            'templates': [
                'templates/base',
                'templates/v2/plugin_data/'
            ],
            'loader': loaders.loader_v2.LoaderV2,
            'validator': validators.validator_v2.ValidatorV2,
            'builder': builders.BuildPluginV2
        },
        '1.0.0': {
            'version': '1.0.0',
            'templates': [
                'templates/base',
                'templates/v1/'
            ],
            'loader': loaders.loader_v1.LoaderV1,
            'validator': validators.validator_v1.ValidatorV1,
            'builder': builders.BuildPluginV1
        }
    }
    data = mapping.get(version, None)

    if not data:
        raise errors.WrongPackageVersionError(
            'Wrong package version "{0}"'.format(version))
    return data


def get_version_mapping_from_plugin(plugin_metadata_path):
    """Returns mapping for specific version of the plugin

    :param str plugin_metadata_path: path to the directory with metadata.yaml file
    :returns: dict which contains
              'version' - package version
              'validator' - validator class
              'templates' - path to templates
              'builder' - builder class
    """
    from fuel_plugin_builder import loaders
    from fuel_plugin_builder import errors
    try:
        meta, report = loaders.LoaderV5().load(plugin_metadata_path)
    except:
        raise errors.WrongPluginDirectoryError(
            'Wrong path to the plugin, cannot find "%s" file', 'metadata.yaml')

    package_version = meta.get('package_version')

    return get_plugin_for_version(package_version)


def get_validator(plugin_path):
    validator = get_version_mapping_from_plugin(plugin_path)['validator']
    return validator(plugin_path)
