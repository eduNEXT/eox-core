#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom Support API permissions module
"""
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions, permissions

from eox_core.api.support.v1.authentication import JWTsignedOauthAppAuthentication


class EoxCoreSupportAPIPermission(permissions.BasePermission):
    """
    Defines a custom permissions to access eox-core API
    These permissions make sure that a token is created with the client credentials of the same site is being used on.
    """

    def has_permission(self, request, view):
        """
        Grants access if:
        1) The user was authenticated via the signed JWT token (AnonymousUser but authenticated).
        2) The user is authenticated and is a staff user.
        """
        if isinstance(request.user, AnonymousUser):
            auth_class_used = getattr(request.successful_authenticator, "__class__", None)
            if auth_class_used == JWTsignedOauthAppAuthentication:
                return True

        if request.user.is_staff:
            return True

        # To prevent leaking important information we return the most basic message.
        raise exceptions.NotAuthenticated(detail="Invalid token")
