name: provisioning
tasks:
  - id: provision
    type: puppet
    version: 2.0.0
    roles: "*"
    parameters:
      puppet_manifest: "provision.pp"
      puppet_modules: "."
      timeout: 3600
      retries: 10
