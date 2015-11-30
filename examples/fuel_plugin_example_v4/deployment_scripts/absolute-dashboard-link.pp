notice('PLUGIN: fuel_plugin_example_v4/absolute-dashboard-link.pp')

$cluster_id = hiera('deployment_id')
$master_ip = hiera('master_ip')
$network_metadata = hiera_hash('network_metadata', {})
$os_public_vip = $network_metadata['vips']['public']['ipaddr']

$dashboard_name = 'Demo Plugin Dashboard #1'
$dashboard_desc = 'A Sample Absolute Dashboard Link'
$dashboard_link = "http://${os_public_vip}/dashboard"

$json_hash = { title       => $dashboard_name,
               description => $dashboard_desc,
               url         => $dashboard_link, }

$json_message = inline_template('<%= require "json"; JSON.dump(@json_hash) %>')

exec { 'create_dashboard_link':
  command => "/usr/bin/curl -H 'Content-Type: application/json' -X POST \
-d '${json_message}' \
http://${master_ip}:8000/api/clusters/${cluster_id}/plugin_links",
}
