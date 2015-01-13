$fuel_settings = parseyaml($astute_settings_yaml)

# Fetch fencing policy and settings
$fence_policy = $::fuel_settings['ha_fencing']['fence_policy']
$fencing_enabled  = $fence_policy ? { 'disabled'=>false, 'reboot'=>true, 'poweroff'=>true, default=>false }

if $fencing_enabled {
  $fencing_settings = parseyaml($fencing_settings_yaml)
  $fence_primitives = $::fencing_settings['fence_primitives']
  $fence_topology   = $::fencing_settings['fence_topology']

  $nodes_hash = $::fuel_settings['nodes']
  $controllers = concat(filter_nodes($nodes_hash,'role','primary-controller'), filter_nodes($nodes_hash,'role','controller'))

  include stdlib
  class { '::pcs_fencing::fencing_primitives':
    fence_primitives => $fence_primitives,
    fence_topology   => $fence_topology,
    nodes            => $controllers,
  }
}
