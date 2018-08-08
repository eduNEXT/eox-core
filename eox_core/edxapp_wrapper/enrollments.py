#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Users public function definitions
"""

from importlib import import_module
from django.conf import settings


def create_enrollment(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.create_enrollment(*args, **kwargs)


def check_edxapp_account_conflicts(*args, **kwargs):
    """ Checks the db for accounts with the same email or password """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.check_edxapp_enrollment_conflicts(*args, **kwargs)
