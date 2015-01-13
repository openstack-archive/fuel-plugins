# Creates fencing primitives and topology for given nodes.
# Assumes all nodes have the same OS installed
#
class pcs_fencing::fencing_primitives (
  $fence_primitives,
  $fence_topology,
  $nodes,
) {
  case $::osfamily {
    'RedHat': {
       $names = filter_hash($nodes, 'fqdn')
    }
    'Debian': {
       $names = filter_hash($nodes, 'name')
    }
    default: {
      fail("Unsupported osfamily: ${::osfamily} operatingsystem: ${::operatingsystem}, module ${module_name} only support osfamily RedHat and Debian")
    }
  }

  anchor {'Fencing primitives start':}
  anchor {'Fencing primitives end':}

  create_resources('::pcs_fencing::fencing', $fence_primitives)

  cs_fencetopo { 'fencing_topology':
    ensure         => present,
    fence_topology => $fence_topology,
    nodes          => $names,
  }
  cs_property { 'stonith-enabled': value  => 'true' }
  cs_property { 'cluster-recheck-interval':  value  => '3min' }
  package {'fence-agents':}

  Anchor['Fencing primitives start'] ->
  Package['fence-agents'] ->
  Pcs_fencing::Fencing<||> ->
  Cs_fencetopo['fencing_topology'] ->
  Cs_property<||> ->
  Anchor['Fencing primitives end']
}
