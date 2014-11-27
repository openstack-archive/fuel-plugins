#
class cindergfs::params {

  $cinder_conf = '/etc/cinder/cinder.conf'

  if $::osfamily == 'Debian' {
    $glusterfs_package_name = 'glusterfs-client'
    $package_name           = 'cinder-volume'
    $volume_service_name    = 'cinder-volume'

  } elsif($::osfamily == 'RedHat') {
    $glusterfs_package_name = 'glusterfs-fuse'
    $package_name           = 'openstack-cinder'
    $volume_service_name    = 'openstack-cinder-volume'

  } else {
    fail("unsuported osfamily ${::osfamily}, currently Debian and Redhat are the only supported platforms")
  }
}
