notice('MODULAR: detach-keystone/controller-keystone.pp')

$access_hash      = hiera_hash('access',{})
$service_endpoint = hiera('service_endpoint')

$admin_tenant     = $access_hash['tenant']
$admin_email      = $access_hash['email']
$admin_user       = $access_hash['user']
$admin_password   = $access_hash['password']
$region           = hiera('region', 'RegionOne')

$murano_settings_hash = hiera('murano_settings', {})
if has_key($murano_settings_hash, 'murano_repo_url') {
  $murano_repo_url = $murano_settings_hash['murano_repo_url']
} else {
  $murano_repo_url = 'http://storage.apps.openstack.org'
}

class { 'openstack::auth_file':
  admin_user      => $admin_user,
  admin_password  => $admin_password,
  admin_tenant    => $admin_tenant,
  region_name     => $region,
  controller_node => $service_endpoint,
  murano_repo_url => $murano_repo_url,
}

