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
from fuel_plugin_builder import utils

logger = logging.getLogger(__name__)


class ValidatorBase(object):
    """Base Validator.

    New ValidatorBase targeted to plugin package version >= 5.0.0 and using
    Checks to describe custom logic and providing output based on
    utils.ReportNode class.

    Check is a basic logic unit that performing validations with given
    parameters.
    """

    package_version = '0.0.1'
    minimal_fuel_version = '0.1'

    def validate(self, data_tree):
        """Validate data tree and return report.

        :param data_tree: plugin data tree starting from the metadata.yaml dict
        :type data_tree: dict

        :return: report
        :rtype: utils.ReportNode
        """

        report = utils.ReportNode('Validating data')
        return report
