# These tasks will be merged into deployment graph. Here you
# can specify new tasks for any roles, even built-in ones.

- id: ${plugin_name}
  type: group
  role: [${plugin_name}]
  parameters:
    strategy:
      type: parallel

- id: ${plugin_name}-deployment-puppet
  type: puppet
  groups: [${plugin_name}]
  required_for: [deploy_end]
  requires: [deploy_start]
  parameters:
    puppet_manifest: "deploy.pp"
    puppet_modules: "."
    timeout: 3600

#- id: ${plugin_name}-post-deployment-sh
#  type: shell
#  role: [${plugin_name}]
#  required_for: [post_deployment_end]
#  requires: [post_deployment_start]
#  parameters:
#    cmd: echo post_deployment_task_executed > /tmp/post_deployment
#    retries: 3
#    interval: 20
#    timeout: 180

#- id: ${plugin_name}-pre-deployment-sh
#  type: shell
#  role: [${plugin_name}]
#  required_for: [pre_deployment_end]
#  requires: [pre_deployment_start]
#  parameters:
#    cmd: echo pre_deployment_task_executed > /tmp/pre_deployment
#    retries: 3
#    interval: 20
#    timeout: 180
