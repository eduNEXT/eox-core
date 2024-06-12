#!/bin/bash

# This script installs the package in the edxapp environment, installs test requirements from Open edX and runs the tests using the Tutor settings.
echo "Install package"
pip install -e /openedx/eox-core
python manage.py lms makemigrations
python manage.py lms migrate

echo "Install test-requirements"
make test-requirements

echo "Run tests"
pytest -s --ds=lms.envs.tutor.test /openedx/eox-core/eox_core/tests/tutor
