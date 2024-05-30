#!/bin/bash

# Install the package in the edxapp env
echo "Install package"
pip install -e ../eox-core

# Install test requirements from openedx
echo "Install test-requirements"
make test-requirements

# Running the tests using the tutor settings
echo "Run tests"
pytest -s --ds=lms.envs.tutor.test /openedx/eox-core/eox_core/tests/tutor
