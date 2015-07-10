# This tasks will be merged in deployment graph, here
# you can also specify new(from this plugin) and core roles

- id: ${plugin_name}
  type: group
  role: [${plugin_name}]

- id: fuel_plugin_example_v3-deployment-sh
  type: shell
  groups: [${plugin_name}]
  required_for: [deploy_end]
  requires: [deploy_start]
  parameters:
    cmd: deploy.sh
    retries: 3
    interval: 20
    timeout: 180

#- id: fuel_plugin_example_v3-deployment-puppet
#  type: puppet
#  groups: [${plugin_name}]
#  required_for: [deploy_end]
#  requires: [deploy_start]
#  parameters:
#    puppet_manifest: "deploy.pp"
#    puppet_modules: ""
#    timeout: 3600