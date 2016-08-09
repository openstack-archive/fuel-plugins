name: deletion
tasks:
  - id: delete
    type: puppet
    version: 2.1.0
    roles:
      - deleted
    parameters:
      puppet_manifest: "delete.pp"
      puppet_modules: "."
      timeout: 3600
      retries: 10
