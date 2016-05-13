# -*- coding: utf-8 -*-

#    Copyright 2016 Mirantis, Inc.
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

import re
from sre_constants import error as sre_error

import jsonschema
import six

from fuel_plugin_builder import errors


class FormatChecker(jsonschema.FormatChecker):

    def __init__(self, role_patterns=(), *args, **kwargs):
        super(FormatChecker, self).__init__()

        @self.checks('fuel_task_role_format')
        def _validate_role(instance):
            sre_msg = None
            if isinstance(instance, six.string_types):
                if instance.startswith('/') and instance.endswith('/'):
                    try:
                        re.compile(instance[1:-1])
                        return True
                    except sre_error as e:
                        sre_msg = str(e)
                else:
                    for role_pattern in role_patterns:
                        if re.match(role_pattern, instance):
                            return True
                err_msg = "Role field should be either a valid " \
                          "regexp enclosed by " \
                          "slashes or a string of '{0}' or an " \
                          "array of those. " \
                          "Got '{1}' instead.".format(", ".join(role_patterns),
                                                      instance)
                if sre_msg:
                    err_msg += "SRE error: \"{0}\"".format(sre_msg)
                raise errors.TaskFieldError(err_msg)
