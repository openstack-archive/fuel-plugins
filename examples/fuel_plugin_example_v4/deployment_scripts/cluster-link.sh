#!/bin/bash
set -eux

# It's a script which creates a custom dashboard link
CLUSTER_ID=`hiera deployment_id`
MASTER_IP=`hiera master_ip`
CLUSTER_LINK="http://localhost/dashboard"

function dashboard_link {
curl -H "Content-Type: application/json" -X POST \
-d '{"title":"Dashboard","description":"A Sample Dashboard Link","url":"${CLUSTER_LINK}"}' \
http://${MASTER_IP}:8000/api/clusters/${CLUSTER_ID}/plugin_links
}

dashboard_link
