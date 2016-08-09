name: network_veification
tasks:
  - id: verify_networks
    type: puppet
    version: 2.1.0
    roles: ["*", "master"]
    required_for: ["deploy_start"]
    parameters:
      puppet_manifest: "delete.pp"
      puppet_modules: "."
      timeout: 3600
      retries: 10
