#
# == Class: redis::main
#
# Installs and configures Redis
#

class redis::main (
  $parallel_syncs          = '1',
  $quorum                  = '1',
  $down_after_milliseconds = '30000',
  $failover_timeout        = '60000',
  $redis_timeout           = '5',
  $redis_port              = '6379',
  $redis_sentinel_port     = '26379',
) {

  $fuel_settings            = parseyaml($astute_settings_yaml)
  $primary_controller       = $fuel_settings['role'] ? { 'primary-controller'=>true, default=>false }
  $nodes_hash               = $fuel_settings['nodes']
  $primary_controller_nodes = filter_nodes($nodes_hash,'role','primary-controller')
  $primary_controller_node  = $primary_controller_nodes[0]['internal_address']
  $controllers              = concat($primary_controller_nodes, filter_nodes($nodes_hash,'role','controller'))
  $internal_addresses       = nodes_to_hash($controllers,'name','internal_address')
  $controller_nodes         = ipsort(values($internal_addresses))
  $management_vip           = $fuel_settings['management_vip']

  include ceilometer::params
  include redis::params

  case $::osfamily {
    'RedHat': {
      $manage_upstart_scripts = false
    }
    'Debian': {
      $manage_upstart_scripts = true
    }
    default: {
      fail("Unsupported osfamily: ${::osfamily} operatingsystem: \
${::operatingsystem}, module ${module_name} only support osfamily \
RedHat and Debian")
    }
  }

  firewall {'120 redis_port':
    port   => $redis_port,
    proto  => 'tcp',
    action => 'accept',
  }

  firewall {'121 redis_sentinel_port':
    port   => $redis_sentinel_port,
    proto  => 'tcp',
    action => 'accept',
  }

  if $primary_controller {
    $conf_slaveof = undef
  } else {
    $conf_slaveof = "$primary_controller_node 6379"
  }

  class { '::redis':
    conf_slave_read_only => 'no',
    service_enable       => false,
    service_ensure       => 'stopped',
    conf_slaveof         => $conf_slaveof,
  }

  $sentinel_confs = sentinel_confs($controller_nodes, $quorum, $parallel_syncs, $down_after_milliseconds, $failover_timeout)

  class { redis::sentinel:
    conf_port              => '26379',
    sentinel_confs         => $sentinel_confs,
    manage_upstart_scripts => $manage_upstart_scripts,
  }

  package {'python-kazoo':
    ensure => 'latest',
  }
  package {'python-redis':
    ensure => 'latest',
  }
  package {'python-tooz':
    ensure => 'latest',
  }

  #redis_backend_url($controller_nodes, $redis_timeout)
  ceilometer_config {
    'coordination/backend_url' : value => "redis://${management_vip}:6379";
    'coordination/heartbeat'   : value => '1.0';
  }

  if $primary {
    exec {'remove_old_resource_central_agent':
      path    => '/usr/sbin:/usr/bin:/sbin:/bin',
      command => 'pcs resource delete p_ceilometer-agent-central --wait=120',
      onlyif  => 'pcs resource show p_ceilometer-agent-central > /dev/null 2>&1',
    }

    Exec['remove_old_resource_central_agent'] -> Cluster::Corosync::Cs_service['ceilometer-agent-central']
  }

  exec {'ocf_script':
    command => "cp /etc/puppet/modules/ceilometer/files/ocf/ceilometer-agent-central /etc/puppet/modules/cluster/files/ocf/",
    path => "/bin:/usr/bin",
  }

  file {'redis_ocf_script':
    path   => "/etc/puppet/modules/cluster/files/ocf/redis-server",
    owner   => 'root',
    group  => 'root',
    source => "puppet:///modules/redis/ocf/redis-server"
  }

  cluster::corosync::cs_service {'ceilometer-agent-central':
    ocf_script          => 'ceilometer-agent-central',
    csr_metadata        => undef,
    csr_complex_type    => 'clone',
    csr_ms_metadata     => { 'interleave' => 'true' },
    csr_mon_intr        => '20',
    csr_mon_timeout     => '30',
    csr_timeout         => '60',
    service_name        => $::ceilometer::params::agent_central_service_name,
    package_name        => $::ceilometer::params::agent_central_package_name,
    service_title       => 'ceilometer-agent-central',
    primary             => $primary_controller,
    hasrestart          => false,
  }

  cluster::corosync::cs_service {'redis-server':
    ocf_script          => 'redis-server',
    csr_metadata        => undef,
    csr_complex_type    => 'clone',
    csr_ms_metadata     => { 'interleave' => 'true' },
    csr_mon_intr        => '20',
    csr_mon_timeout     => '30',
    csr_timeout         => '30',
    service_name        => $::redis::params::service,
    package_name        => $::redis::params::package,
    service_title       => 'redis-server',
    primary             => $primary_controller,
    hasrestart          => false,
  }

  Package['python-kazoo'] ->
  Package['python-redis'] ->
  Package['python-tooz'] ->
  Ceilometer_config <||> ->
  Exec['ocf_script'] ->
  File['redis_ocf_script'] ->
  Cluster::Corosync::Cs_service['redis-server'] ->
  Cluster::Corosync::Cs_service['ceilometer-agent-central']

  if !$primary_controller {
    exec {'waiting-for-central-agent':
      tries     => 10,
      try_sleep => 30,
      command   => "pcs resource show p_${::ceilometer::params::agent_central_service_name} > /dev/null 2>&1",
      path      => '/usr/sbin:/usr/bin:/sbin:/bin',
    }

    exec {'waiting-for-agent-up-on-primary':
      tries     => 10,
      try_sleep => 30,
      command   => "pcs resource | grep -A 1 p_${::ceilometer::params::agent_central_service_name} | grep Started > /dev/null 2>&1",
      path      => '/usr/sbin:/usr/bin:/sbin:/bin',
    }

    exec {'waiting-for-redis-up-on-primary':
      tries     => 10,
      try_sleep => 30,
      command   => "pcs resource | grep -A 1 p_${::redis::params::service} | grep Started > /dev/null 2>&1",
      path      => '/usr/sbin:/usr/bin:/sbin:/bin',
    }

    service {"p_${::ceilometer::params::agent_central_service_name}":
      enable     => true,
      ensure     => 'running',
      hasstatus  => true,
      hasrestart => true,
      provider   => 'pacemaker',
    }

    service {"p_${::redis::params::service}":
      enable     => true,
      ensure     => 'running',
      hasstatus  => true,
      hasrestart => true,
      provider   => 'pacemaker',
    }

    Exec['waiting-for-redis-up-on-primary'] ->
    Service["p_${::redis::params::service}"] ->
    Cluster::Corosync::Cs_service['redis-server'] ->
    Exec['waiting-for-central-agent'] ->
    Exec['waiting-for-agent-up-on-primary'] ->
    Cluster::Corosync::Cs_service['ceilometer-agent-central'] ->
    Service["p_${::ceilometer::params::agent_central_service_name}"]
  }

  service { 'ceilometer-agent-central':
    ensure  => 'stopped',
    name    => $::ceilometer::params::agent_central_service_name,
    enable  => false,
  }
}
