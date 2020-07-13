#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Storages public function definitions
"""
from importlib import import_module

from django.conf import settings


def get_edxapp_production_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform production staticfiles storage
    """
    backend_function = settings.EOX_CORE_STORAGES_BACKEND
    backend = import_module(backend_function)

    return backend.get_edxapp_production_staticfiles_storage()


def get_edxapp_development_staticfiles_storage():  # pylint: disable=invalid-name
    """
    Return the edx-platform production staticfiles storage
    """
    backend_function = settings.EOX_CORE_STORAGES_BACKEND
    backend = import_module(backend_function)

    return backend.get_edxapp_development_staticfiles_storage()
