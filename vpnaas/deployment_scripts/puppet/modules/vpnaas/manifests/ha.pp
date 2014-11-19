#This class is intended to deploy VPNaaS in HA mode.

class vpnaas::ha {

    include vpnaas::params
    include neutron::params


    $fuel_settings      = parseyaml($astute_settings_yaml)
    $access_hash        = $fuel_settings['access']
    $neutron_config     = $fuel_settings['quantum_settings']
    $multiple_agents    = true
    $primary_controller = $fuel_settings['role'] ? { 'primary-controller'=>true, default=>false }

    $debug                    = true
    $verbose                  = true
    $syslog                   = $::use_syslog
    $plugin_config            = '/etc/neutron/l3_agent.ini'


    file {'q-agent-cleanup.py':
      path   => '/usr/bin/q-agent-cleanup.py',
      mode   => '0755',
      owner  => root,
      group  => root,
      source => "puppet:///modules/vpnaas/q-agent-cleanup.py",
    }

    class {'vpnaas::agent':
      manage_service => true,
      enabled        => false,
    }

    if $primary_controller {
      exec { "remove-l3-agent":
        path    => "/sbin:/usr/bin:/usr/sbin:/bin",
        command => "pcs resource delete p_neutron-l3-agent --wait=120",
        onlyif  => "pcs resource show p_neutron-l3-agent > /dev/null 2>&1",
      }
      Exec['remove-l3-agent'] -> Class['vpnaas::agent']
    }
    else {
      exec {'waiting-for-l3-deletion':
        tries     => 5,
        try_sleep => 30,
        command   => "pcs resource show p_neutron-l3-agent > /dev/null 2>&1",
        path      => '/usr/sbin:/usr/bin:/sbin:/bin',
        returns   => [1],
      }
      Exec['waiting-for-l3-deletion'] -> Class['vpnaas::agent']
    }

  if $multiple_agents {
    $csr_metadata = undef
    $csr_multistate_hash = { 'type' => 'clone' }
    $csr_ms_metadata     = { 'interleave' => 'true' }
  } else {
    $csr_metadata        = { 'resource-stickiness' => '1' }
    $csr_multistate_hash = undef
    $csr_ms_metadata     = undef
  }

  $vpnaas_agent_package = $::neutron::params::vpnaas_agent_package ? {
    false   => $::neutron::params::package_name,
    default => $::neutron::params::vpnaas_agent_package,
  }

  cluster::corosync::cs_service {'vpn':
    ocf_script      => 'neutron-agent-vpn',
    csr_parameters  => {
      'debug'           => $debug,
      'syslog'          => $syslog,
      'plugin_config'   => $plugin_config,
      'os_auth_url'     => "http://${fuel_settings['management_vip']}:35357/v2.0/",
      'tenant'          => 'services',
      'username'        => undef,
      'password'        => $neutron_config['keystone']['admin_password'],
      'multiple_agents' => $multiple_agents,
    },
    csr_metadata        => $csr_metadata,
    csr_multistate_hash => $csr_multistate_hash,
    csr_ms_metadata     => $csr_ms_metadata,
    csr_mon_intr    => '20',
    csr_mon_timeout => '10',
    csr_timeout     => '60',
    service_name    => $::neutron::params::vpnaas_agent_service,
    package_name    => $vpnaas_agent_package,
    service_title   => 'neutron-vpnaas-service',
    primary         => $primary_controller,
    hasrestart      => false,
  }

    cluster::corosync::cs_with_service {'vpn-and-ovs':
      first   => "clone_p_${neutron::params::ovs_agent_service}",
      second  => $multiple_agents ? {
                    false   => "p_${neutron::params::vpnaas_agent_service}",
                    default => "clone_p_${neutron::params::vpnaas_agent_service}"
                 },
    }

    if ! $multiple_agents {
      cs_colocation { 'vpn-keepaway-dhcp':
        ensure     => present,
        score      => '-100',
        primitives => [
          "p_${neutron::params::dhcp_agent_service}",
          "p_${neutron::params::vpnaas_agent_service}"
        ],
        require => Cluster::Corosync::Cs_service['vpn'],
      }
    }

    File['q-agent-cleanup.py'] -> Cluster::Corosync::Cs_service["vpn"]

    File["${vpnaas::params::vpn_agent_ocf_file}"] -> Cluster::Corosync::Cs_service["vpn"] ->
    Cluster::Corosync::Cs_with_service['vpn-and-ovs'] -> Class['vpnaas::common']

#fuel-plugins system doesn't have 'primary-controller' role so
#we have to separate controllers' deployment here using waiting cycles.
    if ! $primary_controller {
      exec {'waiting-for-vpn-agent':
        tries     => 10,
        try_sleep => 30,
        command   => "pcs resource show p_neutron-vpn-agent > /dev/null 2>&1",
        path      => '/usr/sbin:/usr/bin:/sbin:/bin',
      }
      Exec['waiting-for-vpn-agent'] -> Cluster::Corosync::Cs_service["vpn"]
    }

    file { "${vpnaas::params::vpn_agent_ocf_file}":
      mode   => 644,
      owner  => root,
      group  => root,
      source => "puppet:///modules/vpnaas/ocf/neutron-agent-vpn"
    }

    class {'vpnaas::common':}


}
