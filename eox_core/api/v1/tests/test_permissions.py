#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for the permissions class
"""
from django.test import TestCase
from mock import MagicMock
from rest_framework.exceptions import NotAuthenticated

from ..permissions import EoxCoreAPIPermission


class PermissionsTest(TestCase):
    """ Tests for the API permissions """

    def test_permissions_for_staff(self):
        """ Staff always passes """
        request = MagicMock()
        request.user.is_staff = True

        has_perm = EoxCoreAPIPermission().has_permission(request, MagicMock())

        self.assertTrue(has_perm)

    def test_read_user_permissions(self):
        """ If the auth does not fail, it comes down to the has_permission result """
        request = MagicMock()
        request.user.is_staff = False
        request.user.has_perm.return_value = False

        has_perm = EoxCoreAPIPermission().has_permission(request, MagicMock())

        self.assertFalse(has_perm)

    def test_permissions_without_auth(self):
        """ If anything in the auth fails, the NotAuthenticated exception is raised """
        request = MagicMock()
        request.user.is_staff = False
        request.user.has_perm.return_value = False
        request.auth = None

        with self.assertRaises(NotAuthenticated):
            EoxCoreAPIPermission().has_permission(request, MagicMock())

    def test_permissions_auth_dop(self):
        """ Authorize the domain via the client.url """
        request = MagicMock()
        request.user.is_staff = False
        request.user.has_perm.return_value = True
        request.get_host.return_value = "domain.com"
        request.auth.client.url = "https://domain.com/"

        has_perm = EoxCoreAPIPermission().has_permission(request, MagicMock())

        self.assertTrue(has_perm)

    def test_permissions_auth_dot(self):
        """ Authorize the domain via the application.allowed_uris """
        request = MagicMock()
        request.user.is_staff = False
        request.user.has_perm.return_value = True
        request.auth.application.redirect_uri_allowed.return_value = True

        has_perm = EoxCoreAPIPermission().has_permission(request, MagicMock())

        self.assertTrue(has_perm)
