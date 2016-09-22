# This puppet manifest creates example file in /tmp folder.

notice('PLUGIN: fuel_plugin_example_v4 - deploy.pp')

class fuel_plugin_example_v4 {
  file { '/tmp/fuel_plugin_example_v4_puppet':
      owner   => 'root',
      group   => 'root',
      mode    => 0644,
      content => "fuel_plugin_example_v4\n",
  }
}

class {'fuel_plugin_example_v4': }
