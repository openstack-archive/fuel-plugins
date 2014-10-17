# Just apply glusterfs volumes
class { 'cindergfs::volume::glusterfs':
		glusterfs_shares => ['10.108.0.117:/gv0'],
	 }