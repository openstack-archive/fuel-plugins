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
---------------

For production versions of plugins, including certified plugins, see
`Released Plugins Catalog`_.

For instructions on installing Fuel plugins, see `Installing Plugins`_.


Finding documentation
---------------------

You can find Fuel Plugins documentation in the following sources:

* Development issues - `Plugins Wiki`_ page.
* Common installation instructions - `Install Fuel Plugins`_ and
  `CLI command reference`_ sections in the User Guide.
* Specific installation instructions - `Fuel Plugins Catalog`_.


OpenStack Fuel-plugins Repository
---------------------------------

This repository contains plugin example, and the Fuel plugin builder tool
(fpb). The plugin code here might not be suitable for production use please
see `Released Plugins Catalog`_  to download release versions of these and
other Fuel plugins.


Creating your own plugins
-------------------------

Detailed instructions can be found in the `Plugins Wiki`_ page.

Plugins should be built using the ``fuel-plugin-builder`` (fpb) utility
found in this repoistory or via ``pip``. ``fbp`` will ensure that build
steps as well as validation is performed prior to assembling a package.

Abbreviated instructions:

.. code:: bash

   pip install fuel-plugin-builder
   fpb --create fuel_plugin_name
   fpb --build <path to plugin>

This will:

* install fuel-plugin-builder
* clone the fuel_plugin_example plugin with the name fuel_plugin_name
* build the plugin ``.rpm`` package.

Examples
````````

Simple Fuel plugin examples you can find here:

https://github.com/openstack/fuel-plugins/tree/master/examples

Other Plugin repositories
`````````````````````````

Other locations known to have Fuel plugins. *Note, these may not be supported
by the Fuel team*

* `Community Plugins`_


.. _Released Plugins Catalog: https://www.fuel-infra.org/plugins/catalog.html
.. _Installing Plugins: https://wiki.openstack.org/wiki/Fuel/Plugins#Installation_procedure
.. _Plugins Wiki: http://wiki.openstack.org/Fuel/Plugins
.. _Install Fuel Plugins: http://docs.mirantis.com/openstack/fuel/fuel-master/user-guide.html#install-fuel-plugins
.. _CLI command reference: http://docs.mirantis.com/openstack/fuel/fuel-master/user-guide.html#fuel-plugins-cli
.. _Fuel Plugins Catalog: https://software.mirantis.com/download-mirantis-openstack-fuel-plug-ins/
.. _Community Plugins: https://github.com/openstack/?query=fuel-plugin
