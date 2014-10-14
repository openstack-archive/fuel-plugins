#!/bin/bash

plugin_name=${plugin_name}-${plugin_version}
repo_path=/var/www/nailgun
plugin_path=$repo_path/plugins/$plugin_name

rm -rf  $plugin_path
mkdir -p $plugin_path
cp -rf * $plugin_path/

python register_plugin.py ${plugin_name}
