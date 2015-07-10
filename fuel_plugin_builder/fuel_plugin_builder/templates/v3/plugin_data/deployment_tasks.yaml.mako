# These tasks will be merged in deployment graph. Here
# you can specify new tasks for this plugin and core roles

- id: ${plugin_name}
  type: group
  role: [${plugin_name}]

- id: ${plugin_name}-deployment-sh
  type: shell
  groups: [${plugin_name}]
  required_for: [deploy_end]
  requires: [deploy_start]
  parameters:
    cmd: deploy.sh
    retries: 3
    interval: 20
    timeout: 180

#- id: ${plugin_name}-deployment-puppet
#  type: puppet
#  groups: [${plugin_name}]
#  required_for: [deploy_end]
#  requires: [deploy_start]
#  parameters:
#    puppet_manifest: "deploy.pp"
#    puppet_modules: ""
#    timeout: 3600