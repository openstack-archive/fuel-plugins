class vpnaas {

    service { 'disable-neutron-l3-service':
      ensure  => stopped,
      name    => "neutron-l3-agent",
      enable  => false,
    }

    Service['disable-neutron-l3-service'] -> Class['vpnaas::agent']

    class {'vpnaas::agent':}
    class {'vpnaas::common':}
}
