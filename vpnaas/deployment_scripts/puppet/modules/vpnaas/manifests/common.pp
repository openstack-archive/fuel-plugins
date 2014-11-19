class vpnaas::common {

    include vpnaas::params

    service { $vpnaas::params::dashboard_service:
      ensure  => running,
      enable  => true,
    }

    exec { "enable_vpnaas_dashboard":
      command => "/bin/sed -i \"s/'enable_vpn': False/'enable_vpn': True/\" $vpnaas::params::dashboard_settings",
      unless  => "/bin/egrep \"'enable_vpn': True\" $vpnaas::params::dashboard_settings",
    }

    service { $vpnaas::params::server_service:
      ensure  => running,
      enable  => true,
    }

    neutron_config {
      'DEFAULT/service_plugins':  value => 'router,vpnaas,metering';
    }

    Neutron_config<||>                    ~> Service[$vpnaas::params::server_service]
    Exec['enable_vpnaas_dashboard']       ~> Service[$vpnaas::params::dashboard_service]
}
