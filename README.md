Fuel Plugins
============
Starting with version 6.0, Fuel supports a Pluggable architecture.

Fuel plugins allow you to install and configure additional capabilities for
your cloud, such as additional storage types and networking functionality.
For example, a Load Balancing as a Service (LBaaS) plugin allows you to add
network load balancing functionality to your cloud so that incoming traffic
can be spread across multiple nodes.  Or you might want to use a GlusterFS
plugin so that you can use a Gluster file system as backend for Cinder
volumes.

Finding Plugins
===============

For production versions of plugins, including certified plugins, see
[Released Plugins Catalog](https://software.mirantis.com/download-mirantis-openstack-fuel-plug-ins/ "Released Plugins Catalog")

StackForge Fuel-plugins Repository
==================================

Structure
---------
This repository contains plugins maintained by the Fuel development team.
Additionally it contains an example plugin, and the Fuel plugin builder tool
(fpb). The plugin code here might not be suitable for production use please
see [Released Plugins Catalog](https://software.mirantis.com/download-mirantis-openstack-fuel-plug-ins/ "Released Plugins Catalog")
to download release versions of these and other Fuel plugins.

* **[fuel_plugin_builder](fuel_plugin_builder)** - the command line interface
that helps to create, check, and build Fuel plugins. You can create your own
plugin in three simple steps:

 * `pip install fuel-plugin-builder`
 * `fpb --create fuel_plugin_name`
 * `fpb --build <path to plugin>`

* **[fuel_plugin_example](fuel_plugin_example)** - simple Fuel plugin example
that shows how you can
create a plugin. It deploys a simple service on your Controller nodes.

* **[lbaas](lbass)** - Fuel plugin that provides
[Neutron LBaaS](https://wiki.openstack.org/wiki/Neutron/LBaaS/PluginDrivers "Neutron LBaaS").

* **[external_glusterfs](external_glusterfs)** - Fuel plugin that allows one to use an existing
[GlusterFS](http://www.gluster.org/documentation/About_Gluster/ "GlusterFS")
cluster as the Cinder backend.

Other Plugin repos
------------------
Other locations known to have Fuel plugins. *Note, these may not be supported
by the Fuel team*

* [Mirantis Plugins](https://github.com/mirantis/fuel-plugins "Mirantis Plugins")

More Information
----------------
For instructions on creating your plugin, see [Plugin Development](http://docs.mirantis.com/openstack/fuel/fuel-6.0/plugin-dev.html "Plugin Development")

For instructions on installing your plugin, see [Installing Plugins](http://docs.mirantis.com/openstack/fuel/fuel-6.0/user-guide.html#install-fuel-plug-ins "Installing Plugins")

Packages of the development version of plugins (CI artifacts) in this repo
can be found at
[Fuel CI job]( https://fuel-jenkins.mirantis.com/job/stackforge-master-fuel-plugins/ "Fuel CI job")
