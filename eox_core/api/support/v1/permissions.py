#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom Support API permissions module
"""
from rest_framework import exceptions, permissions


class EoxCoreSupportAPIPermission(permissions.BasePermission):
    """
    Defines a custom permissions to access eox-core API
    These permissions make sure that a token is created with the client credentials of the same site is being used on.
    """

    def has_permission(self, request, view):
        """
        For now, to grant access only checks if the requesting user:
            1) is_staff
        """
        if request.user.is_staff:
            return True

        # To prevent leaking important information we return the most basic message.
        raise exceptions.NotAuthenticated(detail="Invalid token")
