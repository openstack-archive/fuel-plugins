# Plugin name
name: ${plugin_name}
# Human-readable name for your plugin
title: Title for ${plugin_name} plugin
# Plugin version
version: '1.0.0'
# Description
description: Enable to use plugin X for Neutron
# Required fuel version
fuel_version: ['6.0']

# The plugin is compatible with releases in the list
releases:
  - os: ubuntu
    version: 2014.2-6.0
    mode: ['ha', 'multinode']
    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/ubuntu
  - os: centos
    version: 2014.2-6.0
    mode: ['ha', 'multinode']
    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/centos

# Version of plugin package
package_version: '1.0.0'
