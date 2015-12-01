#!/bin/sh

function plugin-link {

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

    LAST_PLUGIN_ID=`fuel plugins -l | grep fuel_plugin_example_v4 | cut -d ' ' -f1`
    if [ "$LAST_PLUGIN_ID" != "" ]; then
        PLUGIN_ID=$LAST_PLUGIN_ID
        echo "Plugin ID is: $PLUGIN_ID"
        curl -H 'Content-Type: application/json' -X POST -d \
'{"title":"Dashboard","description":"A Sample Dashboard Link","url":"dashboard"}' \
http://127.0.0.1:8000/api/v1/plugins/$PLUGIN_ID/links
        return 0
    fi

    sleep 1
    i=$((i++))
done
fi

}

plugin-link &
