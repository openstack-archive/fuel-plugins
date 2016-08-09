# Plugin name
name: ${plugin_name}

# Human-readable name for your plugin
title: Title for ${plugin_name} plugin

# Your plugin version
version: '0.0.1'

# Description
description: Please describe your plugin here

# Version of plugin package
package_version: '5.0.0'

# Required fuel version
fuel_version: ['9.1']

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



# introduce new bundle
releases:
  - name: 'ExampleRelease'                      #required
    description: 'Example Release Description'  #required
    operating_system: 'ubuntu'                  #required, or its alias "os"
    version: '0.0.1'                            #required

    networks_path: metadata/networks.yaml
    volumes_path: metadata/volumes.yaml
    roles_path: metadata/roles.yaml
    network_roles_path: metadata/network_roles.yaml
    components_path: metadata/components.yaml

    attributes_path: attributes/attributes.yaml
    vmware_attributes_path: attributes/vmware.yaml
    node_attributes_path: attributes/node.yaml
    nic_attributes_path: attributes/nic.yaml
    bond_attributes_path: attributes/bond.yaml

    deployment_scripts_path: deployment_scripts/
    repository_path: repositories/ubuntu

    # Fuel will take all .yaml/.json matching the mask or path and merge
    # this tasks under the given graph types.
    graphs:
      - type: deployment
        graph:
          name: deployment-graph-name
          tasks_path: graphs/deployment_tasks.yaml
