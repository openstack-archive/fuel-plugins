$fuel_settings = parseyaml($astute_settings_yaml)

# Just apply glusterfs volumes
class { 'cindergfs::volume::glusterfs':
		glusterfs_shares => $fuel_settings['external_glusterfs']['endpoint'],
	 }
