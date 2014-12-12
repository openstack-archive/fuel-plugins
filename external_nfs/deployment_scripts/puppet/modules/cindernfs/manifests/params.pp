#
class cindernfs::params {

  $cinder_conf = '/etc/cinder/cinder.conf'

  if $::osfamily == 'Debian' {
    $package_name           = 'cinder-volume'
    $volume_service_name    = 'cinder-volume'

  } elsif($::osfamily == 'RedHat') {
    $package_name           = 'openstack-cinder'
    $volume_service_name    = 'openstack-cinder-volume'

  } else {
    fail("unsuported osfamily ${::osfamily}, currently Debian and Redhat are the only supported platforms")
  }
}
