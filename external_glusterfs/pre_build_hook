#!/bin/bash

set -eux

ROOT="$(dirname `readlink -f $0`)"
MODULES="${ROOT}"/deployment_scripts/puppet/modules
TMP_DIR="${ROOT}"/tmp
mkdir -p "${MODULES}"
mkdir -p "${TMP_DIR}"
REPO_PATH='https://github.com/stackforge/fuel-library/tarball/f43d885914d74fbd062096763222f350f47480e1'

wget -qO- "${REPO_PATH}" | \
    tar -C "${MODULES}" --strip-components=3 -zxvf - \
    stackforge-fuel-library-f43d885/deployment/puppet/{inifile,stdlib}
