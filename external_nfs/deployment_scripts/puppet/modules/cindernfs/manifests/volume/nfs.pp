#
# == Class: cindernfs::volume::nfs
#
# Configures Cinder to use NFS as a volume driver
#
# === Parameters
#
# [*nfs_shares*]
#   (required) An array of nfs volume locations.
#   Must be an array even if there is only one volume.
#
# [*nfs_sparsed_volumes*]
#   (optional) Whether or not to use sparse (thin) volumes.
#   Defaults to undef which uses the driver's default of "true".
#
# [*nfs_mount_point_base*]
#   (optional) Where to mount the Gluster volumes.
#   Defaults to undef which uses the driver's default of "$state_path/mnt".
#
# [*nfs_shares_config*]
#   (optional) The config file to store the given $nfs_shares.
#   Defaults to '/etc/cinder/shares.conf'
#
# === Examples
#
# class { 'cindernfs::volume::nfs':
#   nfs_shares = ['192.168.1.1:/volumes'],
# }
#
class cindernfs::volume::nfs (
  $nfs_shares,
  $nfs_mount_options = undef,
  $nfs_shares_config = '/etc/cinder/nfsshares',
  $nfs_sparsed_volumes = false,
) {
  include cindernfs::params

  cindernfs::backend::nfs { 'DEFAULT':
    nfs_shares           => $nfs_shares,
    nfs_mount_options    => $nfs_mount_options,
    nfs_shares_config    => $nfs_shares_config,
    nfs_sparsed_volumes  => $nfs_sparsed_volumes,
  }
}
