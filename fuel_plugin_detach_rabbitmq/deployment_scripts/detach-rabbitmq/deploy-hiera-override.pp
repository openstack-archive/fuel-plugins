notice('MODULAR: detach-rabbitmq/deploy-hiera_override.pp')

$detach_rabbitmq_plugin = hiera('detach-rabbitmq', undef)
if ($detach_rabbitmq_plugin) {
  $rabbitmq_role = 'rabbitmq-standalone'
  $network_metadata = hiera_hash('network_metadata')
#lint:ignore:80chars
  $rabbit_nodes = get_nodes_hash_by_roles($network_metadata, [ $rabbitmq_role ])
  $rabbit_address_map = get_node_to_ipaddr_map_by_network_role($rabbit_nodes, 'mgmt/messaging')
  $yaml_additional_config = pick($detach_rabbitmq_plugin['yaml_additional_config'], {})
#lint:endignore
  $amqp_port = hiera('amqp_port', '5673')
  $nodes_hash = hiera('nodes')
  $rabbit_nodes_ips = values($rabbit_address_map)
  $rabbit_nodes_names = keys($rabbit_address_map)
  $settings_hash = parseyaml($yaml_additional_config)

  case hiera('role', 'none') {
    /rabbitmq/: {
      $corosync_roles = [ $rabbitmq_role ]
      $rabbit_enabled = true
      $pacemaker_enabled = false
      $corosync_nodes = $rabbit_nodes
    }
    /controller/: {
      $rabbit_enabled = false
      $pacemaker_enabled = true
    }
    default: {
      $corosync_roles = ['primary-controller', 'controller']
      $rabbit_enabled = true
      $pacemaker_enabled = true
      $corosync_nodes = hiera('controllers')
    }
  }

  $amqp_nodes = $rabbit_nodes_ips
  $amqp_hosts = inline_template("<%= @amqp_nodes.map {|x| x + ':' + @amqp_port}.join ',' %>")

  $calculated_content = inline_template('
amqp_hosts: <%= @amqp_hosts %>
rabbit:
  enabled: <%= @rabbit_enabled %>
  pacemaker: <%= @pacemaker_enabled %>
<% if @corosync_nodes -%>
<% require "yaml" -%>
corosync_nodes:
<%= YAML.dump(@corosync_nodes).sub(/--- *$/,"") %>?
<% end -%>
<% if @corosync_roles -%>
corosync_roles:
<%
@corosync_roles.each do |crole|
%>  - <%= crole %>
<% end -%>
<% end -%>
  ')

###################
  file {'/etc/hiera/override':
    ensure  => directory,
  } ->
  file { '/etc/hiera/override/plugins.yaml':
    ensure  => file,
    content => "${yaml_additional_config}\n${calculated_content}\n",
  }
}
