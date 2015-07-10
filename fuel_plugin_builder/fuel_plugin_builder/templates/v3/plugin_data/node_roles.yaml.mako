${plugin_name}:
  # Role name
  name: "Set here name for role how it should be visible in UI"
  # Role description
  description: "Write description for your role"
  # If primaty then during orchestration this role will be
  # splitted into primary-role and role
  has_primary: false
  # Specify if node where role will be assigned
  # needs public IP address
  public_ip_required: false
  # Weigh that will be used for ordering on fuel UI
  weight: 1000
