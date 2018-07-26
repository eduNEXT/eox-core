# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals

from django.test import TestCase

import eox_core


class TestInfoView(TestCase):
    """ Tests for the eox-info page """

    def test_version_is_present(self):
        response = self.client.get('/eox-core/eox-info')
        self.assertContains(response, eox_core.__version__)
