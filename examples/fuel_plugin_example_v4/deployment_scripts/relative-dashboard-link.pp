notice('PLUGIN: fuel_plugin_example_v4/relative-dashboard-link.pp')

$cluster_id = hiera('deployment_id')
$master_ip = hiera('master_ip')

$dashboard_name = 'Demo Plugin Dashboard #2'
$dashboard_desc = 'A Sample Relative Dashboard Link'
$dashboard_link = "/dashboard"

$json_hash = { title       => $dashboard_name,
               description => $dashboard_desc,
               url         => $dashboard_link, }

$json_message = inline_template('<%= require "json"; JSON.dump(@json_hash) %>')

exec { 'create_dashboard_link':
  command => "/usr/bin/curl -H 'Content-Type: application/json' -X POST \
-d '${json_message}' \
http://${master_ip}:8000/api/clusters/${cluster_id}/plugin_links",
}
