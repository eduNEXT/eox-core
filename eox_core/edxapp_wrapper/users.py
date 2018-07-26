#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Users public function definitions
"""

from importlib import import_module
from django.conf import settings


def create_edxapp_user(*args, **kwargs):

    backend_function = settings.EOX_CORE_USER_CREATION_BACKEND
    backend = import_module(backend_function)

    return backend.create_edxapp_user(*args, **kwargs)
