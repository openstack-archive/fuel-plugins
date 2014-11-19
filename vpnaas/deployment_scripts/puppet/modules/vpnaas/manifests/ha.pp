#This class is intended to deploy VPNaaS in HA mode.
#Here we load some necessary parameters from astute.yaml file
#and call modified product manifests for L3 agent.
#Also we directly call cluster::corosync manifests to setup
#collocation between services.

class vpnaas::ha {

    include vpnaas::params
    include neutron::params


    $fuel_settings      = parseyaml($astute_settings_yaml)
    $access_hash        = $fuel_settings['access']
    $neutron_config     = $fuel_settings['quantum_settings']
    $primary            = true
    $multiple_agents    = true
    $primary_controller = $fuel_settings['role'] ? { 'primary-controller'=>true, default=>false }

    $metadata_port            = 8775
    $send_arp_for_ha          = 8
    $external_network_bridge  = 'br-ex'

    $debug                    = true
    $verbose                  = true
    $syslog                   = $::use_syslog
    $plugin_config            = '/etc/neutron/l3_agent.ini'

    package { 'neutron':
      ensure => present,
      name   => $neutron::params::package_name,
    }

    class {'openstack::network::neutron_agents':
      agents            => ['l3'],
      ha_agents         => $primary_controller ? {true => 'primary', default => 'slave'},
      verbose           => $verbose,
      debug             => $debug,
      shared_secret     => undef,
      admin_password    => $neutron_config['keystone']['admin_password'],
      admin_tenant_name => 'services',
      admin_username    => $access_hash[user],
      auth_url          => "http://${fuel_settings['management_vip']}:35357/v2.0/",

      #l3-agent
      metadata_port           => $metadata_port,
      send_arp_for_ha         => $send_arp_for_ha,
      external_network_bridge => $external_network_bridge,
    }

    cluster::corosync::cs_with_service {'l3-and-ovs':
      first   => "clone_p_${neutron::params::ovs_agent_service}",
      second  => $multiple_agents ? {
                    false   => "p_${neutron::params::l3_agent_service}",
                    default => "clone_p_${neutron::params::l3_agent_service}"
                 },
    }

    if ! $multiple_agents {
      cs_colocation { 'l3-keepaway-dhcp':
        ensure     => present,
        score      => '-100',
        primitives => [
          "p_${neutron::params::dhcp_agent_service}",
          "p_${neutron::params::l3_agent_service}"
        ],
        require => Cluster::Corosync::Cs_service['l3'],
      }
    }

    File["${vpnaas::params::l3_agent_ocf_file}"]     -> Class['openstack::network::neutron_agents'] ->
    Cluster::Corosync::Cs_with_service['l3-and-ovs'] -> Class['vpnaas::common']

#fuel-plugins system doesn't have 'primary-controller' role so
#we have to separate controllers' deployment here using waiting cycles.
    if ! $primary_controller {
      exec {'waiting-for-vpn-agent':
        tries     => 10,
        try_sleep => 60,
        command   => "pcs resource show p_neutron-vpn-agent > /dev/null 2>&1",
        path      => '/usr/sbin:/usr/bin:/sbin:/bin',
      }
      Exec['waiting-for-vpn-agent'] -> Class['openstack::network::neutron_agents']
    }
#We replace L3 agent OCF script with VPN agent script.
    file { "${vpnaas::params::l3_agent_ocf_file}":
      mode   => 644,
      owner  => root,
      group  => root,
      source => "puppet:///modules/vpnaas/neutron-agent-l3"
    }

    class {'vpnaas::common':}


}
