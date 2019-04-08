#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom API permissions module
"""
from rest_framework import permissions
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db.utils import ProgrammingError


def load_permissions():
    """
    Helper method to load a custom permission on DB that will be use to give access
    to eox-core API.
    """
    if settings.EOX_CORE_LOAD_PERMISSIONS:
        try:
            content_type = ContentType.objects.get_for_model(User)
            obj, created = Permission.objects.get_or_create(  # pylint: disable=unused-variable
                codename='can_call_eox_core',
                name='Can access eox-core API',
                content_type=content_type,
            )
        except ProgrammingError:
            # This code runs when the app is loaded, if a migration has not been done a ProgrammingError exception is raised
            # we are bypassing those cases to let migrations run smoothly.
            pass


class EoxCoreAPIPermission(permissions.BasePermission):
    """
    Defines a custom permissions to access eox-core API
    """

    def has_permission(self, request, view):
        """
        To grant accees, checks if the request user either can call eox-core API or if it's an admin user.
        """
        return request.user.has_perm('auth.can_call_eox_core') or request.user.is_staff
