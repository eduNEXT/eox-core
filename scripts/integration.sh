#!/bin/bash

bgreen () { printf "\n\n\e[1m\e[32m" ; $@ ; printf "\e[0m\n\n"; }

# This script installs the package in the edxapp environment, installs test
# requirements from Open edX and runs the tests using the Tutor settings.

# Variables
PACKAGE_PATH=/openedx/eox-core

bgreen echo "Install package"
pip install -e $PACKAGE_PATH

bgreen echo "Install eox-tenant (requirement)"
pip install eox-tenant

bgreen echo "Run migrations"
python manage.py lms makemigrations
python manage.py lms migrate

bgreen echo "Install test requirements"
pip install -r requirements/edx/testing.txt

bgreen echo "Load fixtures"
python manage.py lms loaddata "$PACKAGE_PATH/fixtures/initial_data.json"

bgreen echo "Run integration tests"
pytest -s --ds=eox_core.settings.integration_test \
    "$PACKAGE_PATH/eox_core/api/v1/tests/integration" \
    "$PACKAGE_PATH/eox_core/edxapp_wrapper/tests/integration"
