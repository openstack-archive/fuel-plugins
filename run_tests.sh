#!/bin/bash

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

set -eu


function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run fuel plugin building"
  echo ""
  echo "  -b, --build                 Builds all of the plugins"
  echo "  -B, --no-build              Don't run plugins build"
  echo "  -f, --fpb                   Run tests for fpb"
  echo "  -F, --no-fpb                Don't run tests for fpb"
  echo "  -h, --help                  Print this usage message"
  echo ""
  echo "Note: with no options specified, the script will try to run "
  echo "      all available tests with all available checks."
  exit
}


function process_options {
  for arg in $@; do
    case "$arg" in
      -h|--help) usage;;
      -b|--build) plugins_build=1;;
      -B|--no-build) no_plugins_build=1;;
      -f|--fpb) fpb_tests=1;;
      -F|--no-fpb) no_fpb_tests=1;;
      -*) testropts="$testropts $arg";;
      *) testrargs="$testrargs $arg"
    esac
  done
}

# Settings
ROOT=$(dirname `readlink -f $0`)
FPB_VENV_PATH=${FPB_VENV_PATH:-"${ROOT}/fpb_venv"}
BUILT_PLUGINS_PATH=${BUILT_PLUGINS_PATH:-"${ROOT}/built_plugins"}

# Initialize global variables
plugins_build=0
no_plugins_build=0
fpb_tests=0
no_fpb_tests=0


function run_tests {
  run_cleanup

  # This variable collects all failed tests. It'll be printed in
  # the end of this function as a small statistic for user.
  local errors=""

  # Enable all tests if none was specified skipping all explicitly
  # disabled tests.
  if [[ $plugins_build -eq 0 && \
        $fpb_tests -eq 0 ]]; then

    if [ $no_plugins_build -ne 1 ];  then plugins_build=1;  fi
    if [ $no_fpb_tests -ne 1 ];      then fpb_tests=1;  fi

  fi

  # Run all enabled tests
  if [ $plugins_build -eq 1 ]; then
    echo "Starting plugins build..."
    run_build || errors+=" plugins_build"
  fi

  if [ $fpb_tests -eq 1 ]; then
    echo "Starting fpb testing..."
    run_fpb || errors+=" fpb_tests"
  fi

  if [ -n "$errors" ]; then
    echo Failed tests: $errors
    exit 1
  fi

  exit
}


function run_cleanup {
  find ${ROOT} -type f -name *.pyc -delete
}


function run_fpb {
  local result=0

  pushd "${ROOT}" >> /dev/null
  tox || result=1
  popd >> /dev/null

  return $result
}


# Build all of the plugins with current version of plugins builder
function run_build {
  virtualenv $FPB_VENV_PATH

  # virtualenv has unbound variables
  # disable it during virtualenv usage
  set +u

  source $FPB_VENV_PATH/bin/activate || return 1
  fpb_path="${ROOT}"
  pushd $fpb_path
  pip install .
  popd

  mkdir -p $BUILT_PLUGINS_PATH
  rm -f $BUILT_PLUGINS_PATH/*.fp
  rm -f $BUILT_PLUGINS_PATH/*.rpm

  # Find plugins
  for dir in $ROOT/examples/*/metadata.yaml;
  do
    plugin_dir=$(dirname "${dir}");
    pushd "${plugin_dir}"
    fpb --build "${plugin_dir}" --debug || return 1
    cp *.fp $BUILT_PLUGINS_PATH/
    cp *.rpm $BUILT_PLUGINS_PATH/
    popd
  done

  deactivate
  set -u
  return 0
}

# Parse command line arguments and run the tests
process_options $@
run_tests
