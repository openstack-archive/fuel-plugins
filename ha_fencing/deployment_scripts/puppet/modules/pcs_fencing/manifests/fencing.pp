# == Define: pcs_fencing::fencing
#
# Configure STONITH resources for corosync/pacemaker.
#
define pcs_fencing::fencing (
  $agent_type,
  $parameters    = false,
  $operations    = false,
  $meta          = false,
){
  $res_name = "stonith__${title}__${::hostname}"

  cs_resource { $res_name:
    ensure              => present,
    provided_by         => 'pacemaker',
    primitive_class     => 'stonith',
    primitive_type      => $agent_type,
    parameters          => $parameters,
    operations          => $operations,
    metadata            => $meta,
  }

  cs_location {"location__prohibit__${res_name}":
    node_name  => $::pacemaker_hostname,
    node_score => '-INFINITY',
    primitive  => $res_name,
  }

  cs_location {"location__allow__${res_name}":
    primitive  => $res_name,
    rules     => [
      {
        'score'   => '100',
        'boolean' => '',
        'expressions' => [
          {'attribute'=>"#uname",'operation'=>'ne','value'=>$::pacemaker_hostname},
        ],
      },
    ],
  }
  
  Cs_resource[$res_name] ->
  Cs_location<||>
}
