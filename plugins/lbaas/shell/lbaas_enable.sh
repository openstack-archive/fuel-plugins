#!/bin/bash -e
OS_NAME=''
PKG_NAME=''
HTTP_SERVICE_NAME=''
NCONF='/etc/neutron/neutron.conf'
LBINI='/etc/neutron/lbaas_agent.ini'
SERVICE_PROVIDER='LOADBALANCER:Haproxy:neutron.services.loadbalancer.drivers.haproxy.plugin_driver.HaproxyOnHostPluginDriver:default'
SERVICE_PLUGIN='lbaas'
DEVICE_DRIVER='neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver'
INTERFACE_DRIVER='neutron.agent.linux.interface.OVSInterfaceDriver'
HORIZON_SETTINGS=''
HA='false' # TODO: check if we use OVS

function log {
 echo `date +%H:%M:%S` $1 >> ./lbaas.log
}

log "--------------------------"
log "LBaaS-related work started"
# check that we have neutron
test -f /etc/init.d/neutron-server || ( log "Seems that we don't have neutron on that machine"; exit 1 )

# recognize OS type
if   grep -i CentOS /etc/issue.net >/dev/null; then OS_NAME='centos'; log 'Used OS is CentOS'
elif grep -i Ubuntu /etc/issue.net >/dev/null; then OS_NAME='ubuntu'; log 'Used OS is Ubuntu'
fi

# set variables
function var_set {
# set OS-depended options
  if [ $OS_NAME == 'ubuntu' ]; then
    PKG_NAME='neutron-lbaas-agent'
    HTTP_SERVICE_NAME='apache2'
    HORIZON_SETTINGS='/etc/openstack-dashboard/local_settings.py'
  elif [ $OS_NAME == 'centos' ]; then
    PKG_NAME='' # Actually, we don't need that for CentOS today, cause we install lbaas agent silently with another neutron-related default packages
    HTTP_SERVICE_NAME='httpd'
    HORIZON_SETTINGS='/etc/openstack-dashboard/local_settings'
  fi
}

# LBaaS package install 
function lbaas_install {
  [ "$OS_NAME" == "ubuntu" ] && local installed=`aptitude search $PKG_NAME | awk '{ print $1 }'`
  if [[ "$OS_NAME" == "ubuntu" ]] && [[ $installed != 'i' ]]; then
    log "Package $PKG_NAME not installed, installing it"
    apt-get -y install $PKG_NAME >/dev/null
  elif [ $OS_NAME == 'centos' ]; then # Actually, we don't need that for CentOS today, cause we install lbaas agent silently with another neutron-related default packages
    log "In CentOS we do not need to install lbaas explicitly"
  fi
}

# LBaaS config
function lbaas_config {
  local RC=1
  if [[ "$OS_NAME" == "ubuntu" ]] && ( ! egrep -v '(^#|^$)' $NCONF | egrep $SERVICE_PROVIDER >/dev/null ); then
    sed -i "/\[service_providers\]/a service_provider=$SERVICE_PROVIDER" $NCONF
    log "Service provider added to $NCONF"
    RC=0
  fi
  if ! egrep -v '(^#|^$)' $NCONF | egrep '.*service_plugins.*lbaas'>/dev/null; then
    sed -i "/`egrep -v '(^#|^$)' $NCONF | egrep '.*service_plugins.*'`/ s/$/,lbaas/" $NCONF
    log "Service plugins added to $NCONF"
    RC=0
  fi
  if ! egrep -v '(^#|^$)' $LBINI | egrep ".*$INTERFACE_DRIVER.*">/dev/null; then
    sed -i "/\[DEFAULT\]/a interface_driver = $INTERFACE_DRIVER" $LBINI
    log "Interface driver added to $LBINI"
    RC=0
  fi
  if ! egrep -v '(^#|^$)' $LBINI | egrep ".*$DEVICE_DRIVER.*">/dev/null; then
    sed -i "/\[DEFAULT\]/a device_driver = $DEVICE_DRIVER" $LBINI
    log "Device driver added to $LBINI"
    RC=0
  fi
  if ! egrep "'enable_lb': True" $HORIZON_SETTINGS>/dev/null; then
    sed -i "s/'enable_lb': False/'enable_lb': True/" $HORIZON_SETTINGS
    log "LBaaS enabled in Horizon settings at $HORIZON_SETTINGS"
    RC=0
  fi
  return $RC
}

function services_restart {
  #/etc/init.d/neutron-server restart
  #/etc/init.d/neutron-lbaas-agent restart
  service neutron-server restart >/dev/null && log "neutron-server restarted"
  service neutron-lbaas-agent restart >/dev/null && log "neutron-lbaas-agent restarted"
  service $HTTP_SERVICE_NAME restart >/dev/null && log "$HTTP_SERVICE_NAME restarted"
}

var_set && lbaas_install && lbaas_config && services_restart
log "LBaaS-related work ended"
log "--------------------------"
