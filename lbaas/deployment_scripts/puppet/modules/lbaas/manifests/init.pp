# == Class: lbaas
#
# Full description of class lbaas here.
#
# === Parameters
#
# Document parameters here.
#
# [*sample_parameter*]
#   Explanation of what this parameter affects and what it defaults to.
#   e.g. "Specify one or more upstream ntp servers as an array."
#
# === Variables
#
# Here you should define a list of variables that this module would require.
#
# [*sample_variable*]
#   Explanation of how this variable affects the funtion of this class and if
#   it has a default. e.g. "The parameter enc_ntp_servers must be set by the
#   External Node Classifier as a comma separated list of hostnames." (Note,
#   global variables should be avoided in favor of class parameters as
#   of Puppet 2.6.)
#
# === Examples
#
#  class { 'lbaas':
#    servers => [ 'pool.ntp.org', 'ntp.local.company.com' ],
#  }
#
# === Authors
#
# Author Name <author@domain.com>
#
# === Copyright
#
# Copyright 2014 Your name here, unless otherwise noted.
#
class lbaas {
  include lbaas::params

  package { $lbaas::params::lbaas_package_name:
    ensure => present,
  }

# Actually, we need to define some resource, where we will do this configs and then we will call this resource from here. It need to better split
# configuration part (we will try that package with neutron is anstalled in that defined resource) and we can notify something from resource - e.g.
# we can create notify from that resource to neutron-server service. But now it good in that view.
# if $::osfamily == 'Debian'{
#   neutron_config {
#     "service_providers/service_provider": value => 'LOADBALANCER:Haproxy:neutron.services.loadbalancer.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default';
#   }
# }

# Sorry, that needs to rework, obviously, but I haven't so much time to do it.
  exec { "add_lbaas_plugin":
    command => "/bin/sed -i \"/`egrep -v \'(^#|^$)\' $lbaas::params::neutron_conf_file | egrep \'.*service_plugins.*\'`/ s/$/,lbaas/\" $lbaas::params::neutron_conf_file",
    unless  => "/bin/egrep -v '(^#|^$)' $lbaas::params::neutron_conf_file | egrep '.*service_plugins.*lbaas.*'",
    notify  => Service['neutron-server']
  }

  lbaas_config {
    "DEFAULT/device_driver": value => 'neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver';
    "DEFAULT/interface_driver": value => 'neutron.agent.linux.interface.OVSInterfaceDriver';
    "haproxy/user_group": value => $lbaas::params::usergroup;
  }

# That too should be redesigned, but I'm not sure that I need to write whole new provider to change one string of code.
  exec { "enable_lbaas":
    command => "/bin/sed -i \"s/'enable_lb': False/'enable_lb': True/\" $lbaas::params::horizon_settings_file",
    unless  => "/bin/egrep \"'enable_lb': True\" $lbaas::params::horizon_settings_file",
    notify  => Service[$lbaas::params::httpd_service_name],
  }

  service { 'neutron-server':
    ensure  => running,
    enable  => true,
    require => Package[$lbaas::params::lbaas_package_name],
  }

  service { 'neutron-lbaas-agent':
    ensure  => running,
    enable  => true,
    require => Package[$lbaas::params::lbaas_package_name],
  }

  package { $lbaas::params::haproxy_pkg:
    ensure  => present,
  }

  service { $lbaas::params::httpd_service_name:
    enable  => true,
    ensure  => running,
  }

}
