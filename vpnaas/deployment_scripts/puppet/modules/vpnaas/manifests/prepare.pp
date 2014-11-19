class vpnaas::prepare {

    include vpnaas::params

    $fuel_settings      = parseyaml($astute_settings_yaml)
    $primary_controller = $fuel_settings['role'] ? { 'primary-controller'=>true, default=>false }

    exec { "remove-server-deps":
      path    => "/usr/bin:/usr/sbin:/bin",
      command => "sed \"s/require => Class\[\'neutron\'\],/#require => Class\[\'neutron\'\],/g\" -i $vpnaas::params::l3_manifest_file"
    }

    exec { "patch-neutron-params":
      path    => "/usr/bin:/usr/sbin:/bin",
      command => "sed 's/neutron-l3-agent/neutron-vpn-agent/g' -i $vpnaas::params::neutron_params_file"
    }

    exec { "patch-cleanup-script":
      path    => "/sbin:/usr/bin:/usr/sbin:/bin",
      command => "sed \"s/'l3':   'neutron-l3-agent'/'l3':   'neutron-vpn-agent'/g\" -i $vpnaas::params::cleanup_script_file"
    }

    class {'vpnaas::agent':
      manage_service => true,
      enabled        => false,
    }

    if $primary_controller {
      exec { "remove-l3-agent":
        path    => "/sbin:/usr/bin:/usr/sbin:/bin",
        command => "pcs resource delete p_neutron-l3-agent --wait=120",
      }
      Exec['remove-l3-agent'] -> Class['vpnaas::agent']
    }
    else {
      exec {'waiting-for-l3-deletion':
        tries     => 5,
        try_sleep => 30,
        command   => "pcs resource show p_neutron-l3-agent > /dev/null 2>&1",
        path      => '/usr/sbin:/usr/bin:/sbin:/bin',
        returns   => [1],
      }
      Exec['waiting-for-l3-deletion'] -> Class['vpnaas::agent']
    }
}
