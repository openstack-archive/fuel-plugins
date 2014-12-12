$fuel_settings = parseyaml(file('/etc/astute.yaml'))

# Just apply nfs volumes
class { 'cindernfs::volume::nfs':
  nfs_shares => split($fuel_settings['external_nfs']['endpoint'], ','),
}
