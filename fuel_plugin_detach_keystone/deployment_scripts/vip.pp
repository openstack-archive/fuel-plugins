notice('MODULAR: detach-keystone/vip.pp')

$internal_int             = hiera('internal_int')
$public_int               = hiera('public_int',  undef)
$primary_controller_nodes = hiera('primary_controller_nodes', false)
$network_scheme           = hiera('network_scheme', {})
$keystone_vip             = hiera('keystone_vip')
$keystone_public_vip      = hiera('public_keystone_vip')

#FIXME(bpiotrowski): This netmask data is the same as mgmt network
if (hiera('vip_management_cidr_netmask', false)) {
  $vip_management_cidr_netmask = hiera('vip_management_cidr_netmask')
} else {
  $vip_management_cidr_netmask = netmask_to_cidr($primary_controller_nodes[0]['internal_netmask'])
}

#FIXME(bpiotrowski): This netmask data is the same as public network
if (hiera('vip_management_cidr_netmask', false)) {
  $vip_public_cidr_netmask = hiera('vip_public_cidr_netmask')
} else {
  $vip_public_cidr_netmask = netmask_to_cidr($primary_controller_nodes[0]['public_netmask'])
}

$keystone_vip_data  = {
  namespace      => 'haproxy',
  nic            => $internal_int,
  base_veth      => "${internal_int}-hapr",
  ns_veth        => 'hapr-m',
  ip             => $keystone_vip,
  cidr_netmask   => $vip_management_cidr_netmask,
  gateway        => 'none',
  gateway_metric => '0',
  bridge         => $network_scheme['roles']['management'],
  other_networks => $vip_mgmt_other_nets,
  with_ping      => false,
  ping_host_list => '',
}

cluster::virtual_ip { 'service_endpoint' :
  vip => $keystone_vip_data,
}

$keystone_public_vip_data = {
  namespace            => 'haproxy',
  nic                  => $public_int,
  base_veth            => "${public_int}-hapr",
  ns_veth              => 'hapr-p',
  ip                   => $keystone_public_vip,
  gateway              => $network_scheme['endpoints']['br-ex']['gateway'],
  gateway_metric       => '10',
  cidr_netmask         => $vip_public_cidr_netmask,
  bridge               => $network_scheme['roles']['ex'],
  other_networks       => $vip_publ_other_nets,
}
cluster::virtual_ip { 'public_service_endpoint' :
  vip => $keystone_public_vip_data,
}
