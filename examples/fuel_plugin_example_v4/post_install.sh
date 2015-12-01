#!/bin/sh

PLUGIN_NAME=fuel_plugin_example_v4
DASHBOARD_TITLE=Dashboard
DASHBOARD_DESC="A Sample Dashboard Link"
DASHBOARD_URL="/dashboard"

function obtain_token {

# Request a token for admin user
TENANT_NAME=admin
ADMIN_USERNAME=`python -c "import sys; import yaml; f = open('/etc/fuel/astute.yaml'); astute = yaml.load(f); print astute['FUEL_ACCESS']['user'];"`
ADMIN_PASSWORD=`python -c "import sys; import yaml; f = open('/etc/fuel/astute.yaml'); astute = yaml.load(f); print astute['FUEL_ACCESS']['password'];"`
TENANT_ID=admin

REQUEST="{\"auth\": {\"tenantName\":\"$TENANT_NAME\", \"passwordCredentials\": {\"username\": \"$ADMIN_USERNAME\", \"password\": \"$ADMIN_PASSWORD\"}}}"
RAW_TOKEN=`curl -s -d "$REQUEST" -H "Content-type: application/json" "http://localhost:5000/v2.0/tokens"`
TOKEN=`echo $RAW_TOKEN | python -c "import sys; import json; response = json.loads(sys.stdin.read()); print response['access']['token']['id'];"`

}

function plugin_link {

which fuel > /dev/null
if [[ $? -eq 0 ]]; then

local num_retries=10
local i=0

while true; do
    # Fail if number of retries exeeded
    if [[ $i -gt $((num_retries + 1)) ]]; then
        # Report that plugin not registered
        echo "WARNING: Plugin failed to register before the timeout."
        echo "         Plugin dashboard link will not be added."
        return 1
    fi

    LAST_PLUGIN_ID=`fuel plugins -l | grep $PLUGIN_NAME | cut -d ' ' -f1`
    if [ "$LAST_PLUGIN_ID" != "" ]; then
        PLUGIN_ID=$LAST_PLUGIN_ID
        echo "Plugin ID is: $PLUGIN_ID"
        curl -H 'Content-Type: application/json' -H "X-Auth-Token: $TOKEN" -X POST -d \
"{\"title\":\"$DASHBOARD_TITLE\",\"description\":\"$DASHBOARD_DESC\",\"url\":\"$DASHBOARD_URL\"}" \
http://127.0.0.1:8000/api/v1/plugins/$PLUGIN_ID/links
        return 0
    fi

    sleep 1
    i=$((i++))
done
fi

}

obtain_token
echo $TOKEN

plugin_link &
