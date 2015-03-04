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
[Released Plugins Catalog](https://www.fuel-infra.org/plugins/catalog.html "Released Plugins Catalog")

For instructions on installing Fuel plugins, see
[Installing Plugins](https://wiki.openstack.org/wiki/Fuel/Plugins#Installation_procedure "Installing Plugins")


StackForge Fuel-plugins Repository
==================================

This repository contains plugin example, and the Fuel plugin builder tool
(fpb). The plugin code here might not be suitable for production use please
see [Released Plugins Catalog](https://www.fuel-infra.org/plugins/catalog.html "Released Plugins Catalog")
to download release versions of these and other Fuel plugins.


Creating your own plugins
-------------------------
Detailed instructions can be found in the [Plugin Development Guide](http://docs.mirantis.com/openstack/fuel/fuel-6.0/plugin-dev.html "Plugin Development Guide").


Plugins should be built using the
**[fuel_plugin_builder](fuel_plugin_builder)** (fpb) utility found in this
repoistory or via pip. fbp will ensure that build steps as well as validation
is performed prior to assembling a package.

Abbreviated instructions:

```bash
pip install fuel-plugin-builder
fpb --create fuel_plugin_name
fpb --build <path to plugin>
```

This will:
* install fuel_plugin_builder
* clone the fuel_plugin_example plugin with the name fuel_plugin_name
* build the plugin .rpm package.

Plugins
-------
The following is a list of plugins in this repository. Build Artifacts,
including per-change built packages of these plugins can be found at
[Fuel CI job]( https://fuel-jenkins.mirantis.com/job/stackforge-master-fuel-plugins/ "Fuel CI job")

* **[fuel_plugin_example](fuel_plugin_example)** - simple Fuel plugin example
that shows how you can create a plugin. It deploys a simple service on your Controller nodes.

Other Plugin repositories
-------------------------
Other locations known to have Fuel plugins. *Note, these may not be supported
by the Fuel team*

* [Community Plugins](https://github.com/stackforge/?query=fuel-plugin "Community Plugins")
