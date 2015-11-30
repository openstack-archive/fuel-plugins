notice('PLUGIN: fuel_plugin_example_v4/dashboard-link.pp')

$dashboard_name = 'Plugin Dashboard'
$dashboard_desc = 'A Sample Dashboard Link'

# in case the dashboard is deployed on a separate node
$network_metadata = hiera_hash('network_metadata', {})
$os_public_vip = $network_metadata['vips']['public']['ipaddr']
$dashboard_link = "http://${os_public_vip}/dashboard"

# in case the dashboard is available via the controller VIP
# $dashboard_link = "/dashboard"

$json_hash = { title       => $dashboard_name,
               description => $dashboard_desc,
               url         => $dashboard_link, }
$json_message = inline_template('<%= require "json"; JSON.dump(@json_hash) %>')

$master_ip = hiera('master_ip')
$cluster_id = hiera('deployment_id')

exec { 'create_dashboard_link':
  command => "/usr/bin/curl -H 'Content-Type: application/json' -X POST \
-d '${json_message}' \
http://${master_ip}:8000/api/clusters/${cluster_id}/plugin_links",
}
