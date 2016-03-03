# Plugin name
name: ${plugin_name}
# Human-readable name for your plugin
title: Title for ${plugin_name} plugin
# Plugin version
version: '1.0.0'
# Description
description: Please describe your plugin here
# Required fuel version
fuel_version: ['8.0']
# Specify license of your plugin
licenses: ['Apache License Version 2.0']
# Specify author or company name
authors: ['Specify author or company name']
# A link to the plugin's page
homepage: 'https://github.com/openstack/fuel-plugins'
# Specify a group which your plugin implements, possible options:
# network, storage, storage::cinder, storage::glance, hypervisor,
# equipment
groups: []
# Change `false` to `true` if the plugin can be installed in the environment
# after the deployment.
is_hotpluggable: false

# The plugin is compatible with releases in the list
releases:
  - os: ubuntu
    version: mitaka-9.0
    mode: ['ha']
    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/ubuntu

# Version of plugin package
package_version: '4.0.0'
