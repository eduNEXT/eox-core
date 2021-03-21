#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User model wrapper for cs_comments_service public definition.
"""

from importlib import import_module

from django.conf import settings


def replace_username_cs_user(*args, **kwargs):
    """ Gets the User model wrapper for comments service"""

    backend_function = settings.EOX_CORE_COMMENTS_SERVICE_USERS_BACKEND
    backend = import_module(backend_function)

    return backend.replace_username_cs_user(*args, **kwargs)
