#
class cindernfs::params {

  $cinder_conf = '/etc/cinder/cinder.conf'

  if $::osfamily == 'Debian' {
    $required_packages      = [ 'rpcbind', 'nfs-common', 'libevent-2.0',
                                'libgssglue1', 'libnfsidmap2', 'libtirpc1' ]
    $package_name           = 'cinder-volume'
    $volume_service_name    = 'cinder-volume'

  } elsif($::osfamily == 'RedHat') {
    $required_packages      = [ 'rpcbind', 'nfs-utils', 'nfs-utils-lib',
                                'libevent', 'key-utils', 'libtirpc', 'libgssglue' ]
    $package_name           = 'openstack-cinder'
    $volume_service_name    = 'openstack-cinder-volume'

  } else {
    fail("unsuported osfamily ${::osfamily}, currently Debian and Redhat are the only supported platforms")
  }
}
