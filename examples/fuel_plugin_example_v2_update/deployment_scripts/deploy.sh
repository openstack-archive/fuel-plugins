#!/bin/bash
set -eux

# It's a script which deploys your plugin
echo fuel_plugin_example > /tmp/fuel_plugin_example

OS_NAME=''
if   grep -i CentOS /etc/issue.net >/dev/null; then
    OS_NAME='centos';
elif grep -i Ubuntu /etc/issue.net >/dev/null; then
    OS_NAME='ubuntu';
fi

function install_package {
    if [ $OS_NAME == 'ubuntu' ]; then
        apt-get install -y fuel-simple-service
    elif [ $OS_NAME == 'centos' ]; then
        yum install -y fuel-simple-service
    fi
}

install_package
fuel-simple-service.py &
