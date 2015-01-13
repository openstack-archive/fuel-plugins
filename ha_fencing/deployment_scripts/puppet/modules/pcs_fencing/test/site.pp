node default {
  class { 'pcs_fencing::fencing_primitives':
    fence_primitives => {
      'ipmi_off' => {
        'agent_type' => 'fence_ipmilan',
        'operations' => false,
        'meta'       => false,
        'parameters' => false,
      },
    },
    fence_topology => {
      'node-1' => {
        '1' => [ 'ipmi_off' ],
      }
    },
    nodes => [
      {
        'name' => 'node-1',
        'fqdn' => 'node-1.foo.bar',
        'role' => 'primary-controller',
      },
    ],
  }
}
