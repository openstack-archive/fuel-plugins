# VPNaaS

#### Table of Contents

1. [Overview](#overview)
2. [Module Description - What the module does and why it is useful](#module-description)
3. [Setup - The basics of getting started with VPNaaA](#setup)
    * [What VPNaaS affects](#what-vpnaas-affects)
    * [Beginning with VPNaaS](#beginning-with-vpnaas)
4. [Reference - An under-the-hood peek at what the module is doing and how](#reference)
5. [Limitations - OS compatibility, etc.](#limitations)

## Overview

This is VPNaaS plugin for FUEL, which provides an ability to setup VPNaaS Neuton extention
that introduces VPN feature set.

## Module Description

VPNaaS Neutron extention provides additional functionality for the building VPN
connections based on opensource for IPsec based VPNs using just static routing.
This functionality might be used for setup VPN connetion between two tenats which
are placed in the diffent Openstack environments, for example, between Public and
Private Clouds.

## Setup

### What VPNaaS affects

* This plugin contains OpenSwan package for Ubuntu and CentOS.
* During installation manifests make some modification in Horizon for enable VPNaaS functionality.
* Also this plugin replaces l3-agent on vpn-agent, which completely based on l3-agent and has additional VPN functionality.

### Beginning with VPNaaS

How to use VPNaaS you can find here:
https://www.mirantis.com/blog/mirantis-openstack-express-vpn-service-vpnaas-step-step/

## Reference

Here, list the classes, types, providers, facts, etc contained in your module.
This section should include all of the under-the-hood workings of your module so
people know what the module is touching on their system but don't need to mess
with things. (We are working on automating this section!)

## Limitations

This plugin supports only the following OS: CentOS 6.4 and Ubuntu 12.04.
