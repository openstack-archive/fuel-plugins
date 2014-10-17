class lbaas::params {
  $neutron_conf_file = '/etc/neutron/neutron.conf'
  $lbaas_conf_file = '/etc/neutron/lbaas_agent.ini'
  $haproxy_pkg = 'haproxy'

  if $::osfamily == 'Debian' {
    $httpd_service_name = 'apache2'
    $horizon_settings_file = '/etc/openstack-dashboard/local_settings.py'
    $lbaas_package_name = 'neutron-lbaas-agent'
    $usergroup = 'nogroup'

  } elsif($::osfamily == 'RedHat') {
    $httpd_service_name = 'httpd'
    $horizon_settings_file = '/etc/openstack-dashboard/local_settings'
    $lbaas_package_name = 'openstack-neutron'
    $usergroup = 'nobody'

  } else {
    fail("unsupported family ${::osfamily}")
  }
}
