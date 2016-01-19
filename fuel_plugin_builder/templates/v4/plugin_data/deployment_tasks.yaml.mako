# These tasks will be merged into deployment graph. Here you
# can specify new tasks for any roles, even built-in ones.

- id: ${plugin_name}_role
  type: group
  role: [${plugin_name}_role]
  parameters:
    strategy:
      type: parallel

- id: ${plugin_name}-deployment-puppet
  type: puppet
  role: [${plugin_name}_role]
  requires: [deploy_start]
  required_for: [deploy_end]

## If you want to use task-based deployment that is introduced as experimental
## in fuel v8.0 uncomment code section below this comment and uncomment similar
## sections in tasks below.
## See the example:
## https://github.com/openstack/fuel-plugins/tree/master/examples/fuel_plugin_example_v4_experimental
## for more details.

#  version: 2.0.0              # tasks v2.0.0 is supporting task-based deployment
#   cross-depends:
#     - name: deploy_start
#   cross-depended-by:
#     - name: deploy_end

  parameters:
    puppet_manifest: "deploy.pp"
    puppet_modules: "."
    timeout: 3600

#- id: ${plugin_name}-post-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}_role]
#  requires: [post_deployment_start]
#  required_for: [post_deployment_end]
##  version: 2.0.0
##  cross-depends:
##    - name: post_deployment_start
##  cross-depended-by:
##    - name: post_deployment_end
#  parameters:
#    cmd: echo post_deployment_task_executed > /tmp/post_deployment
#    retries: 3
#    interval: 20
#    timeout: 180

#- id: ${plugin_name}-pre-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}_role]
#  requires: [pre_deployment_start]
#  required_for: [pre_deployment_end]
##  version: 2.0.0
##  cross-depends:
##    - name: pre_deployment_start
##  cross-depended-by:
##    - name: pre_deployment_end
#  parameters:
#    cmd: echo pre_deployment_task_executed > /tmp/pre_deployment
#    retries: 3
#    interval: 20
#    timeout: 180
