node default {

  case $::osfamily {
    #'RedHat': {
    #  package { 'epel-release':
    #    ensure   => present,
    #    source   => 'http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm',
    #    provider => rpm,
    #    before   => Class['redis'],
    #  }
    #}
    'Debian': {
      # redis is on repository
    }
    default: {
      fail("Unsupported osfamily: ${::osfamily} operatingsystem: ${::operatingsystem}, module ${module_name} only support osfamily RedHat and Debian")
    }
  }

  class { 'redis::sentinel':
    conf_port      => '26379',
    sentinel_confs => {
      'mymaster' => {
        'monitor'                 => '127.0.0.1 6379 2',
        'down-after-milliseconds' => '60000',
        'failover-timeout'        => 180000,
        'parallel-syncs'          => '3',
      },
      'resque' => {
        'monitor'                 => '127.0.0.1 6379 4',
        'down-after-milliseconds' => '10000',
        'failover-timeout'        => 180000,
        'parallel-syncs'          => '5',
      }
    }
  }

}
