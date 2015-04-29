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

import argparse
import logging
import six
import sys

from fuel_plugin_builder import actions
from fuel_plugin_builder import errors
from fuel_plugin_builder import messages
from fuel_plugin_builder.validators import ValidatorManager

from fuel_plugin_builder.logger import configure_logger

logger = logging.getLogger(__name__)


def print_err(line):
    sys.stderr.write(six.text_type(line))
    sys.stderr.write('\n')


def handle_exception(exc):
    logger.exception(exc)

    if isinstance(exc, errors.FuelCannotFindCommandError):
        print_err(messages.HEADER)
        print_err(messages.INSTALL_REQUIRED_PACKAGES)

    elif isinstance(exc, errors.ValidationError):
        print_err('Validation failed')
        print_err(exc)

    else:
        print_err('Unexpected error')
        print_err(exc)

    sys.exit(-1)


def parse_args():
    """Parse arguments and return them
    """
    parser = argparse.ArgumentParser(
        description='fpb is a fuel plugin builder which '
        'helps you create plugin for Fuel')

    #TODO(vsharshov): we should move to subcommands instead of
    # exclusive group, because in this case we could not
    # support such behavior [-a xxx | [-b yyy -c zzz]]
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--create', help='create a plugin skeleton',
        type=str, metavar='plugin_name')
    group.add_argument(
        '--build', help='build a plugin',
        type=str, metavar='path_to_directory')
    group.add_argument(
        '--check', help='check that plugin is valid',
        type=str, metavar='path_to_directory')

    parser.add_argument(
        '--debug', help='enable debug mode',
        action="store_true")

    parser.add_argument(
        '--package-version', help='which package version to use',
        type=str)

    result = parser.parse_args()
    package_version_check(result, parser)

    return result


def perform_action(args):
    """Performs an action

    :param args: argparse object
    """
    if args.create:
        actions.CreatePlugin(args.create, args.package_version).run()
        print('Plugin is created')
    elif args.build:
        actions.make_builder(args.build).run()
        print('Plugin is built')
    elif args.check:
        ValidatorManager(args.check).get_validator().validate()
        print('Plugin is valid')


def package_version_check(args, parser):
    """Check exclusive nature of --package-version argument
    """
    if (args.build or args.check) and args.package_version:
        parser.error('--package-version works only with --create')


def main():
    """Entry point
    """
    try:
        args = parse_args()
        configure_logger(debug=args.debug)
        perform_action(args)
    except Exception as exc:
        handle_exception(exc)
