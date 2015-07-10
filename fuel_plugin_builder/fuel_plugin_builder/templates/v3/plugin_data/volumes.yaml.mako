volumes:
  # set here new volumes for your role
volumes_roles_mapping:
  ${plugin_name}:
    # Default role mapping
    - {allocate_size: "min", id: "os"}
