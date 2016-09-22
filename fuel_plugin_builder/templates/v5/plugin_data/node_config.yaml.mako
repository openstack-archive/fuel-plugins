# This file contains additional node's attributes provided by plugin.
# Please, take a look at following link for the details:
# - https://blueprints.launchpad.net/fuel/+spec/nics-and-nodes-attributes-via-plugin
# - https://specs.openstack.org/openstack/fuel-specs/specs/10.0/nics-and-nodes-attributes-via-plugin.html

plugin_section_a:
  metadata:
    group: "some_new_section"
    label: "Section A"
  attribute_a:
    label: "Node attribute A for section A"
    description: "Some description"
    type: "text"
    value: ""
  attribute_b:
    label: "Node attribute B for section A"
    description: "Some description"
    type: "checkbox"
    value: ""
