#This class contains common changes both for HA and simple deployment mode.
#It enables VPN tab in Horizon and setups Neutron server.

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

    service { $vpnaas::params::ipsec_service:
      ensure  => running,
      enable  => true,
    }

    Neutron_config<||>                    ~> Service[$vpnaas::params::server_service]
    Exec['enable_vpnaas_dashboard']       ~> Service[$vpnaas::params::dashboard_service]
}
