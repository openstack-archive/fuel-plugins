# -*- coding: utf-8 -*-

#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os
import re

import jinja2
import six
import yaml

import fuel_plugin_builder
from fuel_plugin_builder import consts
from fuel_plugin_builder import errors
from fuel_plugin_builder import utils
from fuel_plugin_builder.actions.base import BaseAction

logger = logging.getLogger(__name__)


class CreatePlugin(BaseAction):
    plugin_name_pattern = re.compile(consts.PLUGIN_NAME_PATTERN)

    def __init__(
            self,
            plugin_path,
            package_version=None,
            fuel_import=False,
            nailgun_path=None,
            library_path=None):
        self.plugin_name = utils.basename(plugin_path.rstrip('/'))
        self.plugin_path = plugin_path
        self.package_version = (package_version or
                                consts.LATEST_VERSION)

        self.fuel_import = fuel_import
        self.nailgun_path = nailgun_path
        self.library_path = library_path

        self.render_ctx = {'plugin_name': self.plugin_name}
        self.template_paths = \
            fuel_plugin_builder.version_mapping.get_plugin_package_config(
                self.package_version)['templates']

    def check(self):
        if utils.is_exists(self.plugin_path):
            raise errors.PluginDirectoryExistsError(
                'Plugins directory {0} already exists, '
                'choose another name'.format(self.plugin_path))

        if not self.plugin_name_pattern.match(self.plugin_name):
            raise errors.ValidationError(
                "Plugin name is invalid, use only lower "
                "case letters, numbers, '_', '-' symbols")

    def run(self):
        report = utils.ReportNode(
            'Start plugin creation "{}"'.format(self.plugin_path))

        # todo(ikutukov): add to report
        self.check()

        for template_path in self.template_paths:
            template_dir = os.path.join(
                os.path.dirname(__file__), '..', template_path)
            report.info('Adding template from {}'.format(template_dir))
            utils.copy(template_dir, self.plugin_path)
            utils.render_files_in_dir(self.plugin_path, self.render_ctx)

        if self.fuel_import:
            report.info("Applying Nailgun configuration")
            report.add_nodes(
                self.import_releases(
                    self.nailgun_path,
                    self.library_path
                )
            )
        else:
            report.info("Creating fresh plugin")

        report.info('Plugin bootstrap is created')
        return report

    def make_release_files_and_metadata(self, release_data, graphs):
        fields = {
            'networks_metadata': 'metadata/networks.yaml',
            'volumes_metadata': 'metadata/volumes.yaml',
            'roles_metadata': 'metadata/roles.yaml',
            'network_roles_metadata': 'metadata/network_roles.yaml',

            'attributes_metadata': 'attributes/attributes.yaml',
            'vmware_attributes_metadata': 'attributes/vmware.yaml',

            'node_attributes_metadata': 'attributes/node.yaml',
            'nic_attributes_metadata': 'attributes/nic.yaml',
            'bond_attributes_metadata': 'attributes/bond.yaml',

            'node_attributes': 'attributes/node.yaml',
        }
        report = utils.ReportNode(
            'Adding release: {}'.format(release_data.get('name')))
        result = {
            'is_release': True,
            'deployment_scripts_path': 'deployment_scripts',
            'repository_path': 'repositories/ubuntu'
        }
        fm = utils.FilesManager()

        def _safe_string(unsafe_string):
            return "".join(
                [c if re.match(r'\w', c) else '-' for c in unsafe_string]
            ).lower()

        for f in release_data:
            if f in fields:
                relative_path = os.path.join(
                    _safe_string(release_data.get('name')),
                    fields[f]
                )
                fm.save(
                    os.path.join(
                        self.plugin_path,
                        relative_path
                    ),
                    release_data[f]
                )
                result[f.replace('_metadata', '') + '_path'] = relative_path
            else:
                # leave it at root metadata
                result[f] = release_data[f]
            result['graphs'] = graphs
        return report.mix_to_data(result)

    def import_releases(self, nailgun_path, library_path):
        report = utils.ReportNode('Importing releases from nailgun')
        if not nailgun_path:
            return report.error('No nailgun path defined')
        if not library_path:
            return report.error('No nailgun library path defined')

        plugin_metadata_path = os.path.join(self.plugin_path, 'metadata.yaml')
        report.info('Using: {}'.format(plugin_metadata_path))

        openstack_file_path = os.path.join(
            nailgun_path, 'fixtures', 'openstack.yaml')
        report.info('Using: {}'.format(openstack_file_path))

        fuel_settings_path = os.path.join(nailgun_path, 'settings.yaml')
        report.info('Using: {}'.format(fuel_settings_path))

        library_tasks_path = os.path.join(library_path, '**/tasks.yaml')
        report.info('Using: {}'.format(library_tasks_path))

        fm = utils.FilesManager()

        library_graphs = []
        library_tasks = fm.load(library_tasks_path) or []
        if library_tasks:
            library_graphs.append({
                'type': 'default',
                'graph': {
                    'name': 'default',
                    'tasks': library_tasks
                }
            })

        for graph in library_graphs:
            graph_path_rel = os.path.join('graphs', graph['type'] + '.yaml')
            fm.save(
                os.path.join(self.plugin_path, graph_path_rel),
                graph.get('graph')
            )
            graph['graph_path'] = graph_path_rel
            del graph['graph']

        fixture = fm.load(openstack_file_path, decode=False)
        nailgun_settings = fm.load(fuel_settings_path)

        # taken from nailgun fixman
        t = jinja2.Template(fixture)
        fixture = yaml.load(
            six.StringIO(t.render(settings=nailgun_settings)))
        for i in range(0, len(fixture)):
            def extend(obj):
                if 'extend' in obj:
                    obj['extend'] = extend(obj['extend'])
                return utils.dict_merge(obj.get('extend', {}), obj)

            fixture[i] = extend(fixture[i])
            fixture[i].pop('extend', None)

        # returning to FPB codebase
        releases_content = [
            r['fields']
            for r in fixture
            if r.get('pk', None) is not None
            ]

        releases_root_metadata = []
        for release_content in releases_content:
            result = self.make_release_files_and_metadata(release_content,
                                                          library_graphs)
            report.add_nodes(result.report)
            releases_root_metadata.append(dict(result))

        report.info('Saving to {}'.format(plugin_metadata_path))
        plugin_metadata = fm.load(plugin_metadata_path)
        plugin_metadata['releases'] = releases_root_metadata
        plugin_metadata['name'] = 'plugin-releases'
        fm.save(plugin_metadata_path, plugin_metadata)

        report.info('Done')
        return report
