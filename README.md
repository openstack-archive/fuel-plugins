Fuel plugins repository
=======================

Starting with version 6.0, Fuel supports Pluggable architecture.
Currently, Cinder and Neutron plugins are available.

* *fuel_plugin_builder* - command line interface which helps to create, check and build Fuel plugin. You can create your own plugin in three simple steps:

 * `pip install fuel-plugin-builder`
 * `fpb --create fuel_plugin_name`
 * `fpb --build fuel_plugin_name`

* *fuel_plugin_example* - simple fuel plugin example which shows how you can create a plugin, it deploys simple service on your Controllers
* *lbaas* - fuel plugin which provides Neutron LBaaS for multinode mode
* *external_glusterfs* - fuel plugin which allows to use existing GlusterFS cluster as Cinder backend

For instructions on creating your plugin, see <link>

For instructions on installing your plugin, see <link>

For production versions plugins, see  <link>

For built development versions plugins, see  <link>
