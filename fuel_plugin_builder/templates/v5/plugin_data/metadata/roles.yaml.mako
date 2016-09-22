${plugin_name}_role:
  # Role name
  name: "Set here the name for the role. This name will be displayed in the Fuel web UI"
  # Role description
  description: "Write description for your role"
  # If primary then during orchestration this role will be
  # separated into primary-role and role
  has_primary: false
  # Assign public IP to node if true
  public_ip_required: false
  # Weight that will be used to sort out the
  # roles on the Fuel web UI
  weight: 1000
