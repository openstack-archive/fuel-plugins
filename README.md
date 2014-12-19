Fuel plugins repository
=======================

Beginning with Mirantis OpenStack 6.0, the deployment manager, Fuel, features the ability to install plug-ins when you deploy your environment.

Fuel plug-ins allow you to install and configure additional capabilities for your cloud, such as additional storage types and networking functionality. For example, a Load Balancing as a Service (LBaaS) plug-in allows you to add network load balancing functionality to your cloud so that incoming traffic can be spread across multiple nodes.  Or you might want to use a GlusterFS plug-in so that you can use a Gluster file system as backend storage for blocks (Cinder).

* *fuel_plugin_builder* - command line interface that helps to create, check and build Fuel plugin. You can create your own plugin in three simple steps:

 * `pip install fuel-plugin-builder`
 * `fpb --create fuel_plugin_name`
 * `fpb --build fuel_plugin_name`

* *fuel_plugin_example* - simple Fuel plug-in example that shows how you can create a plug-in. It deploys simple service on your Controller nodes.

* *lbaas* - Fuel plug-in that provides [Neutron LBaaS](https://wiki.openstack.org/wiki/Neutron/LBaaS/PluginDrivers "Neutron LBaaS") for multi-node mode.

* *external_glusterfs* - Fuel plug-in that allows to use existing [GlusterFS](http://www.gluster.org/documentation/About_Gluster/ "GlusterFS") cluster as the Cinder backend.

For instructions on creating your plug-in, see <ADD LINK TO PLUG-IN DEV GUIDE>

For instructions on installing plug-ins, see [Mirantis Plug-ins Catalog]( https://software.mirantis.com/fuel-plugins/ "Mirantis Plug-ins Catalog").

For built development plug-in versions, see [Fuel CI job]( https://fuel-jenkins.mirantis.com/job/stackforge-master-fuel-plugins/ "Fuel CI job")
