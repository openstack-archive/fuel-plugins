#
# == Class: cindergfs::backend::glusterfs
#
# Configures Cinder to use GlusterFS as a volume driver
#
# === Parameters
#
# [*glusterfs_shares*]
#   (required) An array of GlusterFS volume locations.
#   Must be an array even if there is only one volume.
#
# [*volume_backend_name*]
#   (optional) Allows for the volume_backend_name to be separate of $name.
#   Defaults to: $name
#
# [*glusterfs_sparsed_volumes*]
#   (optional) Whether or not to use sparse (thin) volumes.
#   Defaults to undef which uses the driver's default of "true".
#
# [*glusterfs_mount_point_base*]
#   (optional) Where to mount the Gluster volumes.
#   Defaults to undef which uses the driver's default of "$state_path/mnt".
#
# [*glusterfs_shares_config*]
#   (optional) The config file to store the given $glusterfs_shares.
#   Defaults to '/etc/cinder/glusterfs'
#
# === Examples
#
# cindergfs::backend::glusterfs { 'myGluster':
#   glusterfs_shares = ['192.168.1.1:/volumes'],
# }
#
define cindergfs::backend::glusterfs (
  $glusterfs_shares,
  $volume_backend_name        = 'DEFAULT',
  $glusterfs_sparsed_volumes  = undef,
  $glusterfs_mount_point_base = undef,
  $glusterfs_shares_config    = '/etc/cinder/glusterfs',
) {

  $content = join($glusterfs_shares, "\n")

  package { $cindergfs::params::package_name:
    ensure => present,
  }

  package { $cindergfs::params::glusterfs_package_name:
    ensure => present,
  }

  service { $cindergfs::params::volume_service_name:
    ensure => running,
  }

  file { $glusterfs_shares_config:
    content => "${content}\n",
    require => [ Package[$cindergfs::params::package_name],Package[$cindergfs::params::glusterfs_package_name]],
    notify  => Service[$cindergfs::params::volume_service_name],
  }

  cinder_config {
    "${name}/volume_backend_name":  value => $volume_backend_name;
    "${name}/volume_driver":        value => 'cinder.volume.drivers.glusterfs.GlusterfsDriver';
    "${name}/glusterfs_shares_config":    value => $glusterfs_shares_config;
    "${name}/glusterfs_sparsed_volumes":  value => $glusterfs_sparsed_volumes;
    "${name}/glusterfs_mount_point_base": value => $glusterfs_mount_point_base;
  }
}
