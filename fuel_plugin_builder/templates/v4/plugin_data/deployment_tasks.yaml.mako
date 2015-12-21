# These tasks will be merged into deployment graph. Here you
# can specify new tasks for any roles, even built-in ones.

- id: ${plugin_name}
  type: group
  role: [${plugin_name}]
  parameters:
    strategy:
      type: parallel

- id: ${plugin_name}-deployment-puppet
  version: 2.0.0              # task format version
  type: puppet
  groups: [${plugin_name}]
  required_for: [deploy_end]  # for version 1.0 compatibility
  requires: [deploy_start]    # for version 1.0 compatibility
  cross-depended-by:
    - name: deploy_end
  cross-depends:              # version 2.0 dependency
    - name: deploy_start
  parameters:
    puppet_manifest: "deploy.pp"
    puppet_modules: "."
    timeout: 3600

#- id: ${plugin_name}-post-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}]
#  required_for: [post_deployment_end]
#  requires: [post_deployment_start]
#  cross-depended-by:
#    - name: post_deployment_end
#  cross-depends:
#    - name: post_deployment_start
#  parameters:
#    cmd: echo post_deployment_task_executed > /tmp/post_deployment
#    retries: 3
#    interval: 20
#    timeout: 180

#- id: ${plugin_name}-pre-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}]
#  required_for: [pre_deployment_end]
#  requires: [pre_deployment_start]
#  cross-depended-by:
#    - name: pre_deployment_end
#  cross-depends:
#    - name: pre_deployment_start
#  parameters:
#    cmd: echo pre_deployment_task_executed > /tmp/pre_deployment
#    retries: 3
#    interval: 20
#    timeout: 180
