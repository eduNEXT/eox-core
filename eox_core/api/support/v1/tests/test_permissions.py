#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for the Support API permissions class
"""
from django.test import TestCase
from mock import MagicMock
from rest_framework.exceptions import NotAuthenticated

from eox_core.api.support.v1.permissions import EoxCoreSupportAPIPermission


class SupportAPIPermissionsTest(TestCase):
    """ Tests for the Support API permissions """

    def test_permissions_for_staff(self):
        """ If the user is staff, then it always has permission. """
        request = MagicMock()
        request.user.is_staff = True

        has_perm = EoxCoreSupportAPIPermission().has_permission(request, MagicMock())

        self.assertTrue(has_perm)

    def test_permissions_fails(self):
        """ Tests that if the user is not staff, the NotAuthenticated exception is raised """
        request = MagicMock()
        request.user.is_staff = False

        with self.assertRaises(NotAuthenticated):
            EoxCoreSupportAPIPermission().has_permission(request, MagicMock())

    def test_permissions_without_auth(self):
        """ Tests that if the auth fails, the NotAuthenticated exception is raised """
        request = MagicMock()
        request.user.is_staff = False
        request.user.has_perm.return_value = False
        request.auth = None

        with self.assertRaises(NotAuthenticated):
            EoxCoreSupportAPIPermission().has_permission(request, MagicMock())
