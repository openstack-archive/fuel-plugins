#!/bin/bash -e
OS_NAME=''
GFCONF='/etc/cinder/glusterfs'
GFHOST='10.108.0.117'
GF_VOL='cinder-vol-01'
GF_OPT=''
GF_OWN='root:cinder'
GF_MOD='0640'
CICONF='/etc/cinder/cinder.conf'
GF_SHARES_CONF=$GFCONF
VOLUME_DRIVER='cinder.volume.drivers.glusterfs.GlusterfsDriver'
SPARSED_VOLUMES='true'
CINDER_SERVICE_NAME=''
HA='false' # TODO: check if we use OVS

function log {
 echo `date +%H:%M:%S` $1 >> ./glusterfs.log
}

# set variables
function var_set {
# set OS-depended options
  if [ $OS_NAME == 'ubuntu' ]; then
    CINDER_SERVICE_NAME='cinder-volume'
  elif [ $OS_NAME == 'centos' ]; then
    CINDER_SERVICE_NAME='openstack-cinder-volume'
  fi
}

# GlusterFS-related package install
function glusterfs_install {
  if [ "$OS_NAME" == "centos" ]; then
    if ! rpm -qa | grep gluster; then
      rpm -ivh ./gluster*.rpm
      log "GlusterFS-related client packages installed"
    fi
  elif [ "$OS_NAME" == "ubuntu" ]; then
    if ! [[ `dpkg -l | grep glusterfs-client | awk '{print $1}'` == 'ii' ]]; then
      dpkg -i ./gluster*.deb
      log "GlusterFS-related client packages installed"
    fi
  fi
}

# GlusterFS config
function glusterfs_config {
  local RC=1
  if ! egrep -v '(^#|^$)' $CICONF | egrep ".*glusterfs_shares_config.*">/dev/null; then
    sed -i "/^\[DEFAULT\]/a glusterfs_shares_config = $GF_SHARES_CONF" $CICONF
    log "Shares config added to $CICONF"
    RC=0
  else
    log "We already have GlusterFS shares for cinder on that machine"
    exit 1
  fi
  if ! test -f $GFCONF; then
    if [[ "$GF_OPT" == "" ]]; then
      echo "$GFHOST:/$GF_VOL" > $GFCONF
      log "Added GlusterFS volume to $GFCONF"
      RC=0
    else
      echo "$GFHOST:/$GF_VOL -o $GF_OPT" > $GFCONF
      log "Added GlusterFS volume with '$GF_OPT' options to $GFCONF"
      RC=0
    fi
  fi
  if chown $GF_OWN $GFCONF; then
    log "chowned to $GF_OWN on $GFCONF"
    RC=0
  else
    log "unable to chown $GF_OWN on $GFCONF"
  fi
  if chmod $GF_MOD $GFCONF; then
    log "chmoded to $GF_MOD on $GFCONF"
    RC=0
  else
    log "unable to chmod $GF_MOD on $GFCONF"
  fi
  if ! egrep -v '(^#|^$)' $CICONF | egrep ".*volume_driver.*">/dev/null; then
    sed -i "/^\[DEFAULT\]/a volume_driver = $VOLUME_DRIVER" $CICONF
    log "Volume driver config added to $CICONF"
    RC=0
  fi
  return $RC
}

function services_restart {
  service $CINDER_SERVICE_NAME restart >/dev/null && log "$CINDER_SERVICE_NAME restarted"
}


log "------------------------------------------------------"
log "Cinder GlusterFS-related work started"

# recognize OS type
if   grep -i CentOS /etc/issue.net >/dev/null; then OS_NAME='centos'; log 'Used OS is CentOS'
elif grep -i Ubuntu /etc/issue.net >/dev/null; then OS_NAME='ubuntu'; log 'Used OS is Ubuntu'
fi

var_set

# check that we have cinder
[ "$OS_NAME" == "ubuntu" ] && ( test -f /etc/init.d/$CINDER_SERVICE_NAME || ( log "Seems that we don't have cinder on that machine"; exit 1 ))
[ "$OS_NAME" == "centos" ] && ( test -f /etc/init.d/$CINDER_SERVICE_NAME || ( log "Seems that we don't have cinder on that machine"; exit 1 ))

glusterfs_install && glusterfs_config && services_restart

log "Cinder GlusterFS-related work ended"
log "-----------------------------------------------------"
