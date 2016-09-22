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

import six

from fuel_plugin_builder import actions
from fuel_plugin_builder import errors
from fuel_plugin_builder.logger import configure_logger
from fuel_plugin_builder import version_mapping

logger = logging.getLogger(__name__)


def print_err(line):
    sys.stderr.write(six.text_type(line))
    sys.stderr.write('\n')


def handle_exception(exc):
    logger.exception(exc)

    if isinstance(exc, errors.FuelCannotFindCommandError):
        print_err('=' * 50)
        print_err("""
Was not able to find required packages.

If you use Ubuntu, run:

    # sudo apt-get install createrepo rpm dpkg-dev

If you use CentOS, run:

    # yum install createrepo dpkg-devel dpkg-dev rpm rpm-build

""")

    elif isinstance(exc, errors.ValidationError):
        print_err('Validation failed')
        print_err(exc)

    else:
        print_err('Unexpected error')
        print_err(exc)

    sys.exit(-1)


def decode_string(string):
    """Custom type for add_argument method
    """
    return unicode(string, 'utf-8')


def parse_args():
    """Parse arguments and return them
    """
    parser = argparse.ArgumentParser(
        description='fpb is a fuel plugin builder which '
                    'helps you create plugin for Fuel')

    # TODO(vsharshov): we should move to subcommands instead of
    # exclusive group, because in this case we could not
    # support such behavior [-a xxx | [-b yyy -c zzz]]
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--create', help='create a plugin skeleton',
        type=decode_string, metavar='plugin_name')
    group.add_argument(
        '--build', help='build a plugin',
        type=decode_string, metavar='path_to_directory')
    group.add_argument(
        '--check', help='check that plugin is valid',
        type=decode_string, metavar='path_to_directory')

    parser.add_argument(
        '--debug', help='enable debug mode',
        action="store_true")

    parser.add_argument(
        '--package-version', help='which package version to use',
        type=decode_string)

    parser.add_argument(
        '--fuel-import', help='Create plugin from existing releases',
        action="store_true")
    parser.add_argument(
        '--nailgun-path', help='path se existing Nailgun configuration '
                               'to create releases from',
        type=decode_string)
    parser.add_argument(
        '--library-path', help='path se existing Fuel Library repo '
                               'to create releases from',
        type=decode_string)

    result = parser.parse_args()
    package_version_check(result, parser)

    return result


def perform_action(args):
    """Performs an action

    :param args: argparse object
    """
    logger.debug(version_mapping.validators)
    if args.create:
        report = actions.CreatePlugin(
            plugin_path=args.create,
            package_version=args.package_version,
            fuel_import=args.fuel_import,
            nailgun_path=args.nailgun_path,
            library_path=args.library_path
        ).run()
    elif args.build:
        report = actions.make_builder(args.build).run()
    elif args.check:
        report = actions.make_builder(args.check).check()
    else:
        print("Invalid args: {}".format(args))
        return
    print (report)
    print (report.render())


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
