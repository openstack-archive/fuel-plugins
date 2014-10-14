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
import sys

from fuel_plugin_builder import actions
from fuel_plugin_builder import errors
from fuel_plugin_builder import messages

from fuel_plugin_builder.logger import configure_logger

logger = logging.getLogger(__name__)


def handle_exception(exc):
    logger.exception(exc)

    if isinstance(exc, errors.FuelCannotFindCommandError):
        print(messages.header)
        print(messages.install_required_packages)

    sys.exit(-1)


def parse_args():
    """Parse arguments and return them
    """
    parser = argparse.ArgumentParser(
        description='fpb is a fuel plugin builder which '
        'helps you create plugin for Fuel')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--create', help='create a plugin skeleton',
        nargs=1, metavar='plugin_name')
    group.add_argument(
        '--build', help='build a plugin',
        nargs=1, metavar='path_to_directory')
    parser.add_argument(
        '--debug', help='enable debug mode',
        action="store_true")

    return parser.parse_args()


def perform_action(args):
    """Performs an action

    :param args: argparse object
    """

    if args.create:
        plugin_name = args.create[0]
        logger.debug('Start plugin creation "%s"', args.create)
        action = actions.CreatePlugin(plugin_name)
    elif args.build:
        plugin_path = args.build[0]
        logger.debug('Start plugin building "%s"', args.build)
        action = actions.BuildPlugin(plugin_path)

    action.check()
    action.run()


def main():
    """Entry point
    """
    try:
        args = parse_args()
        configure_logger(debug=args.debug)
        perform_action(args)
    except Exception as exc:
        handle_exception(exc)
