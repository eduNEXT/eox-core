#!/bin/bash

bgreen () { printf "\n\n\e[1m\e[32m" ; $@ ; printf "\e[0m\n\n"; }

# This script installs the package in the edxapp environment, installs test
# requirements from Open edX and runs the tests using the Tutor settings.
bgreen echo "Install package"
pip install -e /openedx/eox-core

bgreen echo "Install test-requirements"
make test-requirements

bgreen echo "Install eox-tenant(requirement)"
pip install eox-tenant

# echo "Run migrations"
# python manage.py lms makemigrations
# python manage.py lms migrate

bgreen echo "Run tests"
pytest -s --ds=lms.envs.tutor.test /openedx/eox-core/eox_core/tests/tutor
