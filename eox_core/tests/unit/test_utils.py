#!/usr/bin/python
"""
Test module for Utils
"""
from django.contrib.sites.models import Site
from django.test import TestCase
from mock import patch

from eox_core.utils import fasthash, get_domain_from_oauth_app_uris, get_or_create_site_from_oauth_app_uris


class UtilsTest(TestCase):
    """
    Test the functions included on utils module
    """

    def setUp(self):
        """
        setup.
        """
        super().setUp()
        self.domain_1 = 'test.academy.edunext.io'
        self.domain_2 = 'test.bragi.edunext.io'
        self.site_1 = Site.objects.create(
            domain=self.domain_1,
            name=self.domain_1,
        )
        self.site_2 = Site.objects.create(
            domain=self.domain_2,
            name="Bragi Testing Site",
        )
        self.redirect_uris_http = "http://bragi.localhost:18000/  http://bragi.localhost:18000"
        self.redirect_uris_https = "https://classroomusb.edunext.co https://classroomusb.edunext.co/"

    def test_fasthash_call(self):
        """
        Answers the question: Can we apply the fasthash method?
        """
        test_str = "test_str"
        fasthash(test_str)

    def test_get_domain_from_oauth_app_uris_http_protocol(self):
        """Tests the get_domain_from_oauth_app_uris function
        when the redirect_uris have URLs with http protocol.

        Expected behavior:
            - Returns de domain.
        """
        domain = get_domain_from_oauth_app_uris(self.redirect_uris_http)

        self.assertEqual('bragi.localhost', domain)

    def test_get_domain_from_oauth_app_uris_https_protocol(self):
        """Tests the get_domain_from_oauth_app_uris function
        when the redirect_uris have URLs with https protocol.

        Expected behavior:
            - Returns de domain.
        """
        domain = get_domain_from_oauth_app_uris(self.redirect_uris_https)

        self.assertEqual('classroomusb.edunext.co', domain)

    @patch("eox_core.utils.get_domain_from_oauth_app_uris")
    def test_get_or_create_site_from_oauth_app_uris_existing_site(self, mock_get_domain):
        """Tests the get_or_create_site_from_oauth_app_uris function
        when the redirect_uris are from an existing Django site.

        Expected behavior:
            - Returns de existing site.
        """
        mock_get_domain.return_value = self.domain_1

        site = get_or_create_site_from_oauth_app_uris(self.redirect_uris_https)

        self.assertEqual(self.domain_1, site.domain)
        self.assertEqual(1, Site.objects.filter(domain=self.domain_1).count())
        mock_get_domain.assert_called_once()

    @patch("eox_core.utils.get_domain_from_oauth_app_uris")
    def test_get_or_create_site_from_oauth_app_uris_existing_site_with_different_name(
        self,
        mock_get_domain,
    ):
        """Tests the get_or_create_site_from_oauth_app_uris function
        when the redirect_uris are from an existing Django site.

        Expected behavior:
            - Returns de existing site.
        """
        mock_get_domain.return_value = self.domain_2

        site = get_or_create_site_from_oauth_app_uris(self.redirect_uris_https)

        self.assertEqual(self.domain_2, site.domain)
        self.assertEqual(1, Site.objects.filter(domain=self.domain_2).count())
        mock_get_domain.assert_called_once()

    @patch("eox_core.utils.get_domain_from_oauth_app_uris")
    def test_get_or_create_site_from_oauth_app_uris_new_site(
        self,
        mock_get_domain,
    ):
        """Tests the get_or_create_site_from_oauth_app_uris function
        when the redirect_uris don't have a Django Site.

        Expected behavior:
            - Creates and returns the new site.
        """
        new_site_domain = "new-site.edunext.io"
        mock_get_domain.return_value = new_site_domain

        site = get_or_create_site_from_oauth_app_uris(self.redirect_uris_https)

        self.assertEqual(new_site_domain, site.domain)
        self.assertEqual(1, Site.objects.filter(domain=self.domain_1).count())
        mock_get_domain.assert_called_once()
