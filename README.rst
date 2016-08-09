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


Fuel Plugin Builder <-> Fuel versions mapping:

 Fuel     FPB      Tasks

 6.0  -  1.0.0  -  0.0.0
 6.0  -  1.0.1  -  0.0.0
 6.0  -  1.0.2  -  0.0.1
 6.1  -  2.0.0  -  1.0.0
 6.1  -  2.0.1  -  1.0.0
 6.1  -  2.0.2  -  1.0.0
 6.1  -  2.0.3  -  1.0.0
 6.1  -  2.0.4  -  1.0.0
 6.1  -  2.0.4  -  1.0.0
 7.0  -  3.0.0  -  1.0.1
 8.0  -  4.0.0  -  2.0.0
 8.0  -  4.1.0  -  2.1.0
 9.1  -  5.0.0  -  2.2.0

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
found in this repoistory or via ``pip``. ``fpb`` will ensure that build
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

Fuel Plugin Builder Architecture
--------------------------------

Fuel plugin builder entry point is ./cli.py file that provides cli command
bindings to the ./actions.

Two actions are available:

  * create
    Creating bootstrap plugin file structure using files combining
    templates/* folders defined in ./versions_mapping.py

  * build
    Build plugin package using working directory.

Build involving 5 steps with according modules responsive for this step for
given plugin package version.

  * Preloading (single for all)
  * Loading
  * Validation
    * Data schema checking
  * Package Build

Preloading is about opening metadata.yaml, looking for package version and
choosing appropriate classes using `./version_mapping.py`

Loading is performed by Loader class of given version that are know where to
look for files how understand their formats, how resolve external references
inside data. Loader output is a list/dict tree with metadata.yaml content as
root. Loading report tree is attached to this list/dict structure and based
on report status FPB deciding to continue build process or reject it providing
failure report to developer.

Validation is performed by one of Validator classes located at ./validators
folder, and taking list/dict data tree as input. Validator business logic taking
data tree at parts and applying
@check functions to this branches making report tree (consist of ReportNode)
as output.

JSON Schema checks is the part of validation when we are getting sure that form
of data tree branches or whole tree is valid. We are making plugins for Fuel so
the data  structure schemas is relying on fuel versioning (starting from v6.0)
so you could easily express with which Fuel version your package validation
should be compatible with. You could see this schemas located at ./schemas
folder.

Building itself is a copying of files preserving their permissions
and making `rpm` package based on `metadata.yaml` of your plugin, command line
arguments and `plugin_rpm.spec.mako` with path defined in `rpm_spec_src_path`
builder attribute resolved with this context to plugin_rpm.spec file.

All validation and loading processes are producing reports.
Reports are the tree of ReportNode() instances.
You could write messages with `report_node.error('ERROR!')`,
`report_node.warning('Warning!')`, `report_node.info('Info')` attach one nodes
to another with
`report_node.add_nodes(ReportNode('Im a child!'), ReportNode('Im too!'))`
And, what is the best option, you could render every tree branch as text log
yaml and json documents just calling `print report_branch_node.render('yaml')`.


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
