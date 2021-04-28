#!/usr/bin/python
"""
Tests for the pipeline module used in third party auth.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import MagicMock, PropertyMock, patch

from eox_core.edxapp_wrapper.users import get_user_signup_source
from eox_core.pipeline import (
    assert_user_information,
    check_disconnect_pipeline_enabled,
    create_signup_source_for_new_association,
    ensure_new_user_has_usable_password,
    ensure_user_has_profile,
    ensure_user_has_signup_source,
)

UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name


class EnsureUserPasswordUsableTest(TestCase):
    """
    Test the ensure_new_user_has_usable_password pipeline step.
    """
    def setUp(self):
        self.backend_mock = MagicMock()
        self.user_mock = MagicMock(spec=User)

    @patch('eox_core.pipeline.get_user_attribute')
    def test_new_user_gets_usable_password(self, get_user_attribute_mock):
        """
        A new user with an unusable password will get a new password.
        """
        user_attribute_mock = MagicMock()
        get_user_attribute_mock.return_value = user_attribute_mock
        self.user_mock.has_usable_password.return_value = False
        ensure_new_user_has_usable_password(self.backend_mock, user=self.user_mock, is_new=True)
        self.user_mock.save.assert_called()
        user_attribute_mock.set_user_attribute.assert_called()

    def test_new_user_already_with_usable_password(self):
        """
        A new user that already has an usable password won't be modified.
        """
        self.user_mock.has_usable_password.return_value = True
        ensure_new_user_has_usable_password(self.backend_mock, user=self.user_mock, is_new=True)
        self.user_mock.save.assert_not_called()

    def test_non_new_user(self):
        """
        A non new user won't be modified by this step.
        """
        ensure_new_user_has_usable_password(self.backend_mock, user=self.user_mock, is_new=False)
        self.user_mock.save.assert_not_called()


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


class SignupSourceRegistration(TestCase):
    """Test custom pipeline steps for signup source registration."""

    def setUp(self):
        self.user_mock = MagicMock()
        self.site_mock = MagicMock()

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_signup_source_after_assoc(self, get_request_mock, signup_source_mock):
        """
        This method tests creating a signup source after associating
        a social auth link to the user.

        Expected behavior:
            The signup source is created using the current site and user.
        """
        signup_source_mock.objects.get_or_create.return_value = (MagicMock(), True,)
        get_request_mock.return_value.site = self.site_mock
        kwargs = {
            "new_association": True,
        }

        create_signup_source_for_new_association(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.called_once_with(
            user=self.user_mock,
            site=self.site_mock,
        )

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_ensure_signup_source(self, get_request_mock, signup_source_mock):
        """
        This method tests creating a signup source when the user has a social
        link but does not have the signup source for the current site.

        Expected behavior:
            The signup source is created using the current site and user.
        """
        signup_source_mock.objects.get_or_create.return_value = (MagicMock(), True,)
        get_request_mock.return_value.site = self.site_mock
        kwargs = {}

        ensure_user_has_signup_source(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.called_once_with(
            user=self.user_mock,
            site=self.site_mock,
        )

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_existent_signup_source_after_assoc(self, get_request_mock, signup_source_mock):
        """
        This method tests executing the signup source steps when the user
        already has a signup source for the current site. This is done after a new
        social auth link is created.

        Expected behavior:
            No signup sources are created.
        """
        signup_source_mock.objects.get_or_create.return_value = (MagicMock(), False,)
        get_request_mock.return_value.site = self.site_mock
        kwargs = {
            "new_association": True,
        }

        create_signup_source_for_new_association(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.called_once_with(
            user=self.user_mock,
            site=self.site_mock,
        )

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_ensure_existent_signup_source(self, get_request_mock, signup_source_mock):
        """
        This method tests executing the signup source steps when the user
        already has a signup source for the current site.

        Expected behavior:
            No signup sources are created.
        """
        signup_source_mock.objects.get_or_create.return_value = (MagicMock(), False,)
        get_request_mock.return_value.site = self.site_mock
        kwargs = {}

        ensure_user_has_signup_source(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.called_once_with(
            user=self.user_mock,
            site=self.site_mock,
        )

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_signup_source_during_register_assoc(self, _, signup_source_mock):
        """
        This method tests executing signup source step create_signup_source_for_new_association
        during the registration process.

        Expected behavior:
            No signup sources are created.
        """
        kwargs = {
            "is_new": True,
        }

        create_signup_source_for_new_association(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.get_or_create.assert_not_called()

    @patch("eox_core.pipeline.UserSignupSource")
    @patch("eox_core.pipeline.get_current_request")
    def test_ensure_signup_source_during_register(self, _, signup_source_mock):
        """
        This method tests executing signup source step ensure_user_has_signup_source
        during the registration process.

        Expected behavior:
            No signup sources are created.
        """
        kwargs = {
            "is_new": True,
        }

        ensure_user_has_signup_source(self.user_mock, **kwargs)

        signup_source_mock.objects.get_or_create.assert_not_called()
