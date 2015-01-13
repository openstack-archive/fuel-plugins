pcs_fencing
===========

#### Table of Contents

1. [Overview - What is the pcs_fencing module?](#overview)
2. [Module Description - What does the module do?](#module-description)
3. [Setup - The basics of getting started with pcs_fencing](#setup)
4. [Implementation - An under-the-hood peek at what the module is doing](#implementation)
5. [Limitations - OS compatibility, etc.](#limitations)
6. [Development - Guide for contributing to the module](#development)
7. [Contributors - Those with commits](#contributors)
8. [Release Notes - Notes on the most recent updates to the module](#release-notes)

Overview
--------

TODO(bogdando) provide a link to Fuel plugin repo then ready.
The pcs_fencing module is a part of Fencing plugin for Fuel and have no
a separate code repository.
The module itself is used to configure fencing primitives in Pacemaker
and combine them into the Fencing topology.

Module Description
------------------

The pcs_fencing module is intended to provide STONITH based HA fencing
of the failed nodes in Corosync & Pacemaker cluster. This module
cannot be used separately from Fuel Fencing plugin.
Pcs_fencing module operates the data structures which are tight to the ones
in Fuel YAML configuration file and has no its own parameters.
This module also installs fence-agents package and assumes there is
the one avaiable in the OS repositories.

Setup
-----

### Installing pcs_fencing

This module is being installed automatically as a part of Fuel Fencing
plugin.
The module's rspec tests could be run only after the plugin is built as
its pre build hook will download required Fuel custom puppet module for corosync
and puppetlabs/stdlib module.

### Beginning with pcs_fencing

Instructions for beginning with pcs_fencing will be added later.

Implementation
--------------

### pcs_fencing

pcs_fencing is a combination of Puppet manifest and ruby code to delivery
configuration and extra functionality through custom types, providers, parser
functions and facts from Fuel library of puppet manifests.
Note that it requires a custom module for corosync and includes a custom
provider for fencing topology.

Limitations
-----------

Limitations will be added as they are discovered.

Development
-----------

Developer documentation for the entire Fuel project.

* https://wiki.openstack.org/wiki/Fuel#Where_can_documentation_be_found

Contributors
------------

Will be added later

Versioning
----------

This module is being versioned as well as Fuel Fencing plugin.

Release Notes
-------------

This module has no a separate release notes. See the release notes for
Fuel Fencing plugin.
