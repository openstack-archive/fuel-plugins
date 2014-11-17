Fuel plugins repository
=======================

Starting with version 6.0, Fuel supports Pluggable architecture.
Currently, Cinder and Neutron plugins are available.

* *fuel_plugin_builder* - command line interface that helps to create, check and build Fuel plugin. You can create your own plugin in three simple steps:

 * `pip install fuel-plugin-builder`
 * `fpb --create fuel_plugin_name`
 * `fpb --build fuel_plugin_name`

* *fuel_plugin_example* - simple Fuel plugin example that shows how you can create a plugin. It deploys simple service on your Controller nodes.
* *lbaas* - Fuel plugin that provides Neutron LBaaS for multinode mode.
* *external_glusterfs* - fuel plugin which allows to use existing GlusterFS cluster as the Cinder backend.

For instructions on creating your plugin, see <link>

For instructions on installing your plugin, see <link>

For production plugin versions, see <link>

For built development versions plugins, see <link>
