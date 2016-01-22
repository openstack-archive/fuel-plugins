# These tasks will be merged into deployment graph. Here you
# can specify new tasks for any roles, even built-in ones.
#
# See the examples for plugin package v5.0 to understand tasks description
# format. You can find more info in Fuel Plugin Development Overview:
# https://www.mirantis.com/partners/become-mirantis-unlocked-partner/fuel-plugin-development/

- id: ${plugin_name}-deployment-puppet
  version: 2.0.0
  type: puppet
  role: [${plugin_name}_node_role]
  cross-depends:
    - name: deploy_start
  cross-depended-by:
    - name: deploy_end
  parameters:
    puppet_manifest: "deploy.pp"
    puppet_modules: "."
    timeout: 3600

#- id: ${plugin_name}-post-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}_node_role]
#  cross-depends:
#    - name: post_deployment_start
#  cross-depended-by:
#    - name: post_deployment_end
#  parameters:
#    cmd: echo post_deployment_task_executed > /tmp/post_deployment
#    retries: 3
#    interval: 20
#    timeout: 180

#- id: ${plugin_name}-pre-deployment-sh
#  version: 2.0.0
#  type: shell
#  role: [${plugin_name}_node_role]
#  cross-depends:
#    - name: pre_deployment_start
#  cross-depended-by:
#    - name: pre_deployment_end
#  parameters:
#    cmd: echo pre_deployment_task_executed > /tmp/pre_deployment
#    retries: 3
#    interval: 20
#    timeout: 180
