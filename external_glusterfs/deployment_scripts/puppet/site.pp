$fuel_settings = parseyaml(file('/etc/astute.yaml'))

# Just apply glusterfs volumes
class { 'cindergfs::volume::glusterfs':
		glusterfs_shares => $fuel_settings['external_glusterfs']['endpoint'],
	 }
