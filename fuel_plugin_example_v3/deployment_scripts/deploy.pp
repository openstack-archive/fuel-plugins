notice('PLUGIN: fuel_plugin_example_v3 - deploy.pp')

class fuel_plugin_example_v3 {
  file { '/tmp/fuel_plugin_example_v3_puppet':
      owner   => 'root',
      group   => 'root',
      mode    => 0644,
      content => "fuel_plugin_example_v3\n",
  }
}

class {'fuel_plugin_example_v3': }
