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


HEADER = '=' * 50
INSTALL_REQUIRED_PACKAGES = """
Was not able to find required packages.

If you use Ubuntu, run:

    # sudo apt-get install createrepo rpm dpkg-dev

If you use CentOS, run:

    # yum install createrepo dpkg-devel rpm rpm-build

"""
PLUGIN_WRONG_NAME_EXCEPTION_MESSAGE = ("Plugin name is invalid, use only "
                                       "lower case letters, numbers, '_', '-' "
                                       "symbols")
