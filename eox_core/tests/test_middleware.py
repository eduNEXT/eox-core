#!/usr/bin/python
"""
Test module for the custom Middlewares
"""
import mock
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory, TestCase

from eox_core.middleware import PathRedirectionMiddleware, RedirectionsMiddleware
from eox_core.models import Redirection


class PathRedirectionMiddlewareTest(TestCase):
    """
    Testing the middleware PathRedirectionMiddleware
    """
    def setUp(self):
        """ setup """
        self.request_factory = RequestFactory()
        self.middleware_instance = PathRedirectionMiddleware()

    @mock.patch('eox_core.middleware.PathRedirectionMiddleware.process_mktg_redirect')
    @mock.patch('eox_core.middleware.PathRedirectionMiddleware.process_custom_path_redirect')
    @mock.patch('eox_core.middleware.configuration_helper')
    def test_no_redirection_set(self, conf_help_mock,
                                m_process_custom_path_redirect,
                                m_process_mktg_redirect):
        """
        Test the middleware is not redirecting because EDNX_CUSTOM_PATH_REDIRECTS
        and MKTG_REDIRECTS setting are not set in conf helpers
        """
        request = self.request_factory.get('/custom/path/')
        conf_help_mock.has_override_value.return_value = None
        result = self.middleware_instance.process_request(request)
        conf_help_mock.has_override_value.assert_called()
        m_process_custom_path_redirect.assert_not_called()
        m_process_mktg_redirect.assert_not_called()
        self.assertIsNone(result)

    @mock.patch('eox_core.middleware.configuration_helper')
    def test_empty_redirection_custom(self, conf_help_mock):
        """
        Test the middleware is not redirecting because EDNX_CUSTOM_PATH_REDIRECTS
        setting is set to an empty value.
        """
        request = self.request_factory.get('/custom/path/')
        conf_help_mock.get_value.return_value = {}
        result = self.middleware_instance.process_custom_path_redirect(request)
        conf_help_mock.get_value.assert_called_once()
        self.assertIsNone(result)

    @mock.patch('eox_core.middleware.configuration_helper')
    def test_empty_redirection_mktg(self, conf_help_mock):
        """
        Test the middleware is not redirecting because MKTG_REDIRECTS
        setting is set to an empty value.
        """
        request = self.request_factory.get('/custom/path/')
        conf_help_mock.get_value.return_value = {}
        result = self.middleware_instance.process_mktg_redirect(request)
        conf_help_mock.get_value.assert_called_once()
        self.assertIsNone(result)

    @mock.patch('eox_core.middleware.configuration_helper')
    def test_redirection_not_found(self, conf_help_mock):
        """
        Test if a request with a path associated to the not found value is raising
        a 404 response.
        """
        request = self.request_factory.get('/custom/path/')

        conf_help_mock.has_override_value.return_value = True

        redirection = {
            '/custom/path/': 'not_found'
        }
        conf_help_mock.get_value.return_value = redirection

        try:
            result = self.middleware_instance.process_request(request)
        except Http404:
            pass
        else:
            self.assertEqual(result.status_code, 404)

    @mock.patch('eox_core.middleware.configuration_helper')
    def test_redirection_login_required(self, conf_help_mock):
        """
        Test if a request with a path associated to the login required value is
        being redirected to the /login.
        """

        def has_override_value(value):
            """ Mock configuration helper response. """
            return value == "EDNX_CUSTOM_PATH_REDIRECTS"

        request = self.request_factory.get('/custom/path/')
        request.user = AnonymousUser()
        conf_help_mock.has_override_value.side_effect = has_override_value
        conf_help_mock.get_dict.return_value = {'ednx_custom_login_link': '/login'}
        redirection = {
            '/custom/path/': 'login_required'
        }
        conf_help_mock.get_value.return_value = redirection
        result = self.middleware_instance.process_request(request)
        self.assertIn('/login', result.url)

    @mock.patch('eox_core.middleware.configuration_helper')
    def test_mktg_redirection(self, conf_help_mock):
        """
        Test if a request with a path associated to the mktg redirects is
        being redirected to the correct url.
        """
        def has_override_value(value):
            """ Mock configuration helper response. """
            return value == "MKTG_REDIRECTS"

        request = self.request_factory.get('/tos')

        conf_help_mock.has_override_value.return_value = has_override_value
        target_url = '/host.domain/terms'
        conf_help_mock.get_value.return_value = {'tos.html': target_url}
        result = self.middleware_instance.process_request(request)
        self.assertIn(target_url, result.url)


class RedirectionMiddlewareTest(TestCase):
    """
    Testing the middleware RedirectionsMiddleware.
    """
    def setUp(self):
        """ setup """
        self.request_factory = RequestFactory()
        self.middleware_instance = RedirectionsMiddleware()

    def test_disabled_feature(self):
        """
        Test the usage of the feature flag
        """
        request = self.request_factory.get('/')
        with mock.patch.dict('django.conf.settings.FEATURES', {'USE_REDIRECTION_MIDDLEWARE': False}):
            result = self.middleware_instance.process_request(request)
        self.assertIsNone(result)

    @mock.patch('eox_core.models.Redirection.objects.get')
    def test_domain_without_redirection(self, redirection_get_mock):
        """
        Test the behaviour when the request domain does not have a redirection object.
        """
        request = self.request_factory.get('/')
        redirection_get_mock.side_effect = Redirection.DoesNotExist  # pylint: disable=no-member
        result = self.middleware_instance.process_request(request)
        redirection_get_mock.assert_called_once()
        self.assertIsNone(result)

    @mock.patch('eox_core.models.Redirection.objects.get')
    def test_redirection(self, redirection_get_mock):
        """
        Test the behaviour when the request domain does not have a redirection object.
        """
        request = self.request_factory.get('/', HTTP_HOST='www.example.com')
        redirection = Redirection("www.example.com", 'example.com', 302, 'http')
        redirection_get_mock.return_value = redirection
        result = self.middleware_instance.process_request(request)

        self.assertIsNotNone(result)
