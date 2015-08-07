notice('MODULAR: haproxy-database.pp')

$is_primary_controller    = hiera('primary_controller')
$custom_mysql_setup_class = hiera('custom_mysql_setup_class')
$mysqld_ipaddresses       = hiera('mysqld_ipaddresses')
$mysqld_names             = hiera('mysqld_names')
$database_vip             = hiera('database_vip')

Haproxy::Service        { use_include => true }
Haproxy::Balancermember { use_include => true }

if ($custom_mysql_setup_class in ['galera', 'percona', 'percona_packages']) {
  class { 'openstack::ha::mysqld':
    is_primary_controller => $is_primary_controller,
    server_names          => $mysqld_names,
    ipaddresses           => $mysqld_ipaddresses,
    public_virtual_ip     => $database_vip,
    internal_virtual_ip   => $database_vip,
  }

  #FIXME(mattymo): top level haproxy stats class doesn't listen on this VIP
  class { '::openstack::ha::stats':
    internal_virtual_ip => $database_vip,
    public_virtual_ip   => $database_vip,
  }

}

