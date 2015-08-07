notice('MODULAR: detach-database/virtual_ip.pp')

$internal_int                = hiera('internal_int')
$public_int                  = hiera('public_int',  undef)
$primary_controller_nodes    = hiera('primary_controller_nodes', false)
$network_scheme              = hiera('network_scheme', {})

#FIXME(mattymo): This netmask data is the same as mgmt net
if ( hiera('vip_management_cidr_netmask', false )){
  $vip_management_cidr_netmask = hiera('vip_management_cidr_netmask')
} else {
  $vip_management_cidr_netmask = netmask_to_cidr($primary_controller_nodes[0]['internal_netmask'])
}

$database_vip_data = {
  namespace            => 'haproxy',
  nic                  => $internal_int,
  base_veth            => "${internal_int}-hapr",
  ns_veth              => "hapr-m",
  ip                   => hiera('database_vip'),
  cidr_netmask         => $vip_management_cidr_netmask,
  gateway              => 'none',
  gateway_metric       => '0',
  bridge               => $network_scheme['roles']['management'],
  other_networks       => $vip_mgmt_other_nets,
  with_ping            => false,
  ping_host_list       => "",
}

cluster::virtual_ip { 'database' :
  vip => $database_vip_data,
}

#Not needed (mattymo)
#$management_vips = ['database']
#$vips = $management_vips
## Some topologies might need to keep the vips on the same node during
## deploymenet. This would only need to be changed by hand.
#$keep_vips_together = false
#
#if $keep_vips_together {
#  cs_rsc_colocation { 'ha_vips':
#    ensure      => present,
#    primitives  => [prefix($vips, "vip__")],
#  }
#  Cluster::Virtual_ip[$vips] -> Cs_rsc_colocation['ha_vips']
#}
#

