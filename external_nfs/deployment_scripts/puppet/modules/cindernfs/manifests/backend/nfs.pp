#
# == Class: cindernfs::backend::nfs
#
# Configures Cinder to use NFS as a volume driver
#
# === Parameters
#
# [*nfs_shares*]
#   (required) An array of nfs volume locations.
#   Must be an array even if there is only one volume.
#
# [*volume_backend_name*]
#   (optional) Allows for the volume_backend_name to be separate of $name.
#   Defaults to: $name
#
# [*nfs_mount_options*]
#   (optional) NFS mount points.
#
# [*nfs_shares_config*]
#   (optional) The config file to store the given $nfs_shares.
#   Defaults to '/etc/cinder/nfsshares'
#
# === Examples
#
# cindernfs::backend::nfs { 'myNFS':
#   nfs_shares = ['192.168.1.1:/volumes'],
# }
#
define cindernfs::backend::nfs (
  $nfs_shares,
  $volume_backend_name  = 'DEFAULT',
  $nfs_mount_options    = undef,
  $nfs_shares_config    = '/etc/cinder/nfsshares',
  $nfs_sparsed_volumes  = false,
) {

  $content = join($nfs_shares, "\n")

  package { $cindernfs::params::package_name:
    ensure => present,
  }

  package { $cindernfs::params::required_packages:
    ensure => present,
  }

  service { $cindernfs::params::volume_service_name:
    ensure => running,
  }

  file { $nfs_shares_config:
    content => "${content}\n",
    require => [ Package[$cindernfs::params::package_name], Package[$cindernfs::params::required_packages] ],
    notify  => Service[$cindernfs::params::volume_service_name],
    mode    => 0640,
    owner   => 'root',
    group   => 'cinder',
  }

  cinder_config {
    "${name}/volume_backend_name":  value => $volume_backend_name;
    "${name}/volume_driver":        value => 'cinder.volume.drivers.nfs.NfsDriver';
    "${name}/nfs_shares_config":    value => $nfs_shares_config;
    "${name}/nfs_mount_options":    value => $nfs_mount_options;
    "${name}/nfs_sparsed_volumes":  value => $nfs_sparsed_volumes;
  }
}
