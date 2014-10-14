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

import os
import re

from setuptools import find_packages
from setuptools import setup


def find_requires():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    requirements = []
    with open(u'{0}/requirements.txt'.format(dir_path), 'r') as reqs:
        requirements = reqs.readlines()
    return requirements


setup(
    name='fuel_plugin_builder',
    version='0.1.0',
    description='Helps to create and build fuel plugins',
    long_description="""Helps to create and build fuel plugins""",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: System :: Software Distribution"],
    author='Mirantis Inc.',
    author_email='product@mirantis.com',
    url='http://mirantis.com',
    keywords='fuel plugins plugin',
    packages=find_packages(),
    zip_safe=False,
    install_requires=find_requires(),
    include_package_data=True,
    package_data={'': ['templates/*', 'templates/.gitignore']},
    entry_points={
        'console_scripts': [
            'fpb = fuel_plugin_builder.cli:main']})
