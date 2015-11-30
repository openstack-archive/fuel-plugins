notice('MODULAR: fuel_plugin_example_v4/cluster-link.pp')

$cluster_id = hiera('deployment_id')
$master_ip = hiera('master_ip')
$network_metadata = hiera_hash('network_metadata', {})
$mos_public_vip = $network_metadata['vips']['public']['ipaddr']
$cluster_link = "http://${mos_public_vip}/dashboard"
$json_message = "{\"title\":\"Dashboard\",\"description\":\"A Sample Dashboard Link\",\"url\":\"${cluster_link}\"}"

exec { 'create_cluster_link':
  command => "/usr/bin/curl -H 'Content-Type: application/json' -X POST \
-d '${json_message}' \
http://${master_ip}:8000/api/clusters/${cluster_id}/plugin_links",
}
