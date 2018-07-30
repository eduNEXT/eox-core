# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from ..test_utils import SuperUserFactory, DEFAULT_PASSWORD
import eox_core


class TestInfoView(TestCase):
    """ Tests for the eox-info page """

    def test_version_is_present(self):
        """ Check that test version is present """
        response = self.client.get('/eox-info')
        self.assertContains(response, eox_core.__version__)

    def test_user_is_logged_in(self):
        self.superuser = SuperUserFactory()
        self.client.login(username=self.superuser.username, password=DEFAULT_PASSWORD)
