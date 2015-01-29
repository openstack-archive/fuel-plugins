# Plugin name
name: ${plugin_name}
# Human-readable name for your plugin
title: Title for ${plugin_name} plugin
# Plugin version
version: ${plugin_version}
# Description
description: Enable to use plugin X for Neutron
# Required fuel version
fuel_version: ['6.1']

# The plugin is compatible with releases in the list
releases:
  - os: ubuntu
    version: 2014.2-6.1
    mode: ['ha', 'multinode']
    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/ubuntu
  - os: centos
    version: 2014.2-6.1
    mode: ['ha', 'multinode']
    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/centos

# Version of plugin package
package_version: '2.0.0'
