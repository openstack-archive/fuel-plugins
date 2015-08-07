#!/bin/bash
PLUGIN_DIR=/var/www/nailgun/plugins/%{name}
declare -a roles=(`ls ${PLUGIN_DIR}/deployment_scripts/roles/`)

FUEL='/usr/bin/fuel'
REL=`$FUEL rel | grep -i ubuntu | awk '{print $1}' | head`
FUEL_REL=`$FUEL rel | grep -i ubuntu | awk '{print $NF}'`

#FIXME(mattymo): remove when role-as-a-plugin is merged
function create_roles {
  for role in ${roles[@]}; do
    $FUEL role --rel $REL | awk '{print $1}' | grep -qx ${role%.*}
      if [[ $? -eq 0 ]]; then
        $FUEL role --rel $REL --update --file ${PLUGIN_DIR}/deployment_scripts/roles/${role}
      else
        $FUEL role --rel $REL --create --file ${PLUGIN_DIR}/deployment_scripts/roles/${role}
      fi
  done
}

create_roles
cp -a ${PLUGIN_DIR}/deployment_scripts/detach-rabbitmq /etc/puppet/$FUEL_REL/modules/osnailyfacter/modular/
$FUEL rel --sync-deployment-tasks --dir /etc/puppet/$FUEL_REL

