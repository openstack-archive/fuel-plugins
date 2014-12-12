$fuel_settings = parseyaml(file('/etc/astute.yaml'))

# Just apply nfs volumes
class { 'cindernfs::volume::nfs':
  nfs_shares => split($fuel_settings['external_nfs']['endpoint'], ','),
  nfs_mount_options => $fuel_settings['external_nfs']['mount_options'],
  nfs_sparsed_volumes => $fuel_settings['external_nfs']['sparsed_volumes'],
}
