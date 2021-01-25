#!/usr/bin/python
"""
Tests for the pipeline module used in third party auth.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import MagicMock, PropertyMock, patch

from eox_core.pipeline import assert_user_information, check_disconnect_pipeline_enabled, ensure_user_has_profile


class EnsureUserProfileTest(TestCase):
    """
    Test the custom association backend.
    """
    def setUp(self):
        self.backend_mock = MagicMock()
        self.user_mock = MagicMock()

    @patch('eox_core.edxapp_wrapper.users.import_module')
    def test_user_with_profile_works(self, import_mock):
        """
        A user that already has a profile will do nothing
        """
        backend = MagicMock()
        import_mock.side_effect = backend

        ensure_user_has_profile(self.backend_mock, {}, user=self.user_mock)
        backend().get_user_profile().assert_not_called()

    @patch('eox_core.edxapp_wrapper.users.import_module')
    def test_user_without_profile_works(self, import_mock):
        """
        A user that has no profile will create one
        """
        backend = MagicMock()
        import_mock.side_effect = backend
        backend().get_user_profile().DoesNotExist = ValueError
        type(self.user_mock).profile = PropertyMock(side_effect=ValueError)

        ensure_user_has_profile(self.backend_mock, {}, user=self.user_mock)
        backend().get_user_profile().objects.create.assert_called()


class DisconnectionPipelineTest(TestCase):
    """Test disconnection from TPA provider."""

    def setUp(self):
        self.backend_mock = MagicMock()

    def test_disable_disconnect_pipeline(self):
        """
        Test disabling disconnection pipeline through TPA provider settings.
        """
        self.backend_mock.setting.return_value.get.return_value = True

        with self.assertRaises(Exception):
            check_disconnect_pipeline_enabled(self.backend_mock)

    def test_disconnect_pipeline_enable_explicit(self):
        """
        Test explicitly enable disconnection pipeline through TPA provider settings.
        """
        self.backend_mock.setting.return_value.get.return_value = False

        self.assertIsNone(check_disconnect_pipeline_enabled(self.backend_mock))

    def test_disconnect_pipeline_enable_implicit(self):
        """
        Test enable disconnection pipeline by not defining disable setting through TPA
        provider settings.
        """
        self.backend_mock.setting.return_value.get.return_value = None

        self.assertIsNone(check_disconnect_pipeline_enabled(self.backend_mock))


class ConnectionPipelineTest(TestCase):
    """Test custom pipeline steps for connection to a TPA provider."""

    def setUp(self):
        self.backend_mock = MagicMock()
        self.user_mock = MagicMock(spec=User)
        self.user_mock.email = "test.example.com"
        self.user_mock.username = "test"

    def test_connect_matching_users(self):
        """
        Test connection pipeline when the information from the user from the LMS matches
        the information returned by the TPA provider.
        """
        details = {
            "email": "test.example.com",
            "username": "test",
        }
        self.backend_mock.setting.return_value.get.return_value = ["email", "username"]

        self.assertIsNone(assert_user_information(details, self.user_mock, self.backend_mock))

    def test_connect_unmatching_users(self):
        """
        Test connection pipeline when user's information from the LMS does not match
        the information returned by the TPA provider.
        """
        details = {
            "email": "test.notexample.com",
            "username": "test",
        }
        self.backend_mock.setting.return_value.get.return_value = ["email", "username"]

        with self.assertRaises(Exception):
            assert_user_information(details, self.user_mock, self.backend_mock)

    def test_connect_any_user(self):
        """
        Test connection pipeline when matching fields are not defined. This means that
        does not matter if the users match or not.
        """
        details = {
            "email": "test.notExample.com",
            "username": "testExample",
        }
        self.backend_mock.setting.return_value.get.return_value = []

        self.assertIsNone(assert_user_information(details, self.user_mock, self.backend_mock))
