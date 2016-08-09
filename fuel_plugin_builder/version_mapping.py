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


def get_mapping(version):
    from fuel_plugin_builder import validators
    from fuel_plugin_builder import loaders
    from fuel_plugin_builder.actions import build
    return {
        '5.0.0': {
            'version': '5.0.0',
            'templates': [
                'templates/base',
                'templates/v5/plugin_data/'
            ],

            'loader': loaders.loader_v5.LoaderV5,
            'validator': validators.validator_v5.ValidatorV5,
            'builder': build.BuildPluginV5
        }
    }.get(version, None)
    # {'version': '1.0.0',
    #  'templates': ['templates/base', 'templates/v1/'],
    #  'validator': validators.ValidatorV1,
    #  'builder': build.BuildPluginV1},
    # {'version': '2.0.0',
    #  'templates': ['templates/base', 'templates/v2/plugin_data/'],
    #  'validator': validators.ValidatorV2,
    #  'builder': build.BuildPluginV2},
    # {'version': '3.0.0',
    #  'templates': ['templates/base', 'templates/v3/plugin_data/'],
    #  'validator': validators.ValidatorV3,
    #  'builder': build.BuildPluginV3},
    # {'version': '4.0.0',
    #  'templates': [
    #       'templates/base',
    #       'templates/v3/plugin_data/',
    #       'templates/v4/plugin_data/'
    #   ],
    #  'validator': validators.ValidatorV4,
    #  'builder': build.BuildPluginV4},

    # return [
    #     {'version': '1.0.0',
    #      'templates': ['templates/base', 'templates/v1/'],
    #      'validator': validators.ValidatorV1,
    #      'builder': build.BuildPluginV1},
    #     {'version': '2.0.0',
    #      'templates': ['templates/base', 'templates/v2/plugin_data/'],
    #      'validator': validators.ValidatorV2,
    #      'builder': build.BuildPluginV2},
    #     {'version': '3.0.0',
    #      'templates': ['templates/base', 'templates/v3/plugin_data/'],
    #      'validator': validators.ValidatorV3,
    #      'builder': build.BuildPluginV3},
    #     {'version': '4.0.0',
    #      'templates': [
    #          'templates/base',
    #          'templates/v3/plugin_data/',
    #          'templates/v4/plugin_data/'],
    #      'validator': validators.ValidatorV4,
    #      'builder': build.BuildPluginV4}]


def get_plugin_for_version(version):
    from fuel_plugin_builder import errors
    """Retrieves data which are required for specific version of plugin

    :param str version: version of package
    :returns: dict which contains
              'version' - package version
              'templates' - array of paths to templates
              'validator' - validator class
              'builder' - builder class
    """
    data = get_mapping(version)

    if not data:
        raise errors.WrongPackageVersionError(
            'Wrong package version "{0}"'.format(version))

    return data


def get_version_mapping_from_plugin(plugin_path):
    """Returns mapping for specific version of the plugin

    :param str plugin_path: path to the directory with metadata.yaml file
    :returns: dict which contains
              'version' - package version
              'validator' - validator class
              'templates' - path to templates
              'builder' - builder class
    """
    from fuel_plugin_builder import loaders
    from fuel_plugin_builder import errors

    try:
        meta = loaders.LoaderV5(plugin_path).load('metadata.yaml')
    except:
        raise errors.WrongPluginDirectoryError(
            'Wrong path to the plugin, cannot find "%s" file', 'metadata.yaml')

    package_version = meta.get('package_version')

    return get_plugin_for_version(package_version)
