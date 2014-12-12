#!/bin/bash

OS_NAME=''
if   grep -i CentOS /etc/issue.net >/dev/null; then
    OS_NAME='centos';
elif grep -i Ubuntu /etc/issue.net >/dev/null; then
    OS_NAME='ubuntu';
fi

function install_package {
    if [ $OS_NAME == 'ubuntu' ]; then
        apt-get install -y rpcbind nfs-common libevent-2.0 \
            libgssglue1 libnfsidmap2 libtirpc1
    elif [ $OS_NAME == 'centos' ]; then
        yum install -y rpcbind nfs-utils nfs-utils-lib libevent \
            key-utils libtirpc libgssglue
    fi
}

install_package
