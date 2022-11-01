"""
Test module for the OauthApplicationAPIView class.
"""
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse
from mock import Mock, patch
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from eox_core.api.support.v1.views import User


class OauthApplicationAPIViewTest(APITestCase):  # pylint: disable=too-many-instance-attributes
    """Oauth Application API TestCase."""

    def setUp(self):
        """
        setup.
        """
        super().setUp()
        self.api_user = User(
            username='staff',
            email='staffuser@example.com',
            is_staff=True,
        )
        self.url = reverse('eox-support-api:eox-support-api:edxapp-oauth-application')
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)
        self.site = Site.objects.create(
            domain='testing-site.edunext.io',
            name='testing-site',
        )
        self.user = User.objects.create(
            username='johndoe',
            email='johndoe@example.com',
        )
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission_test_1 = Permission.objects.get_or_create(  # pylint: disable=unused-variable
            codename='test_1',
            name='Can access test-1 API',
            content_type=self.content_type,
        )
        self.permission_test_2 = Permission.objects.get_or_create(  # pylint: disable=unused-variable
            codename='test_2',
            name='Can access test-2 API',
            content_type=self.content_type,
        )

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.UserSignupSource')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_with_new_user(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_user_signup_source,
        mock_get_or_create_site,
    ):
        """Tests the case where an Oauth Application is created
        with a new user.

        Expected behavior:
            - The Oauth App and the User instances are created.
            - Status code 200.
        """
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.side_effect = User.DoesNotExist
        mock_create_edxapp_user.return_value = self.user, ""
        mock_get_user_signup_source.return_value = Mock()
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_1", "test_2"]
            },
            "redirect_uris": "http://testing-site.io/ http://testing-site.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(data["name"], response.data["name"])
        self.assertTrue(self.user.user_permissions.filter(codename="test_1").exists())
        self.assertTrue(self.user.user_permissions.filter(codename="test_2").exists())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_called_once()
        mock_get_or_create_site.assert_called_once()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.UserSignupSource')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_with_existing_user_and_permissions(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_user_signup_source,
        mock_get_or_create_site,
    ):
        """Tests the case where an Oauth Application is created
        with an existing user.

        Expected behavior:
            - The Oauth App is created with the existing user.
            - Status code 200.
        """
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        mock_get_user_signup_source.return_value = Mock()
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_1", "test_2"]
            },
            "redirect_uris": "http://testing-site2.io/ http://testing-site2.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application 2",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(data["name"], response.data["name"])
        self.assertTrue(self.user.user_permissions.filter(codename="test_1").exists())
        self.assertTrue(self.user.user_permissions.filter(codename="test_2").exists())
        self.assertEqual(2, self.user.user_permissions.all().count())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_called_once()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_with_wrong_data(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_or_create_site,
    ):
        """Tests the case where the data sended in the
        request is incomplete or incorrect.

        Expected behavior:
            - Status code 400 BAD REQUEST.
        """
        message = b'{"authorization_grant_type":["This field is required."]}'
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_1", "test_2"]
            },
            "client_type": "confidential",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(message, response.content)
        mock_get_edxapp_user.assert_not_called()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_not_called()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.UserSignupSource')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_with_wrong_permissions_for_user(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_user_signup_source,
        mock_get_or_create_site,
    ):
        """Tests the case where the permissions sent for the user
        don't exist.

        Expected behavior:
            - The Oauth App and the User instances are created,
            but the user has no permissions granted.
            - Status code 200.
        """
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        mock_get_user_signup_source.return_value = Mock()
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_7", "test_8"]
            },
            "redirect_uris": "http://testing-site2.io/ http://testing-site2.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application 3",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(data["name"], response.data["name"])
        self.assertFalse(self.user.user_permissions.filter(codename="test_7").exists())
        self.assertFalse(self.user.user_permissions.filter(codename="test_8").exists())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_called_once()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.UserSignupSource')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_get_existing_oauth_application(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_user_signup_source,
        mock_get_or_create_site,
    ):
        """Tests the case an Oauth Application with the same
        information already exists.

        Expected behavior:
            - Returns the existent Oauth Application.
            - Status code 200.
        """
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        mock_get_user_signup_source.return_value = Mock()
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_1", "test_2"]
            },
            "redirect_uris": "http://testing-site.io/ http://testing-site.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(data["name"], response.data["name"])
        self.assertEqual(1, Application.objects.filter(name=data["name"]).count())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_called_once()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_when_get_or_create_edxapp_user_fails(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_or_create_site,
    ):
        """Tests the case where the methods the get or create
        the edxapp user fails.

        Expected behavior:
            - The Oauth App is not created.
            - Status code 500.
        """
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.side_effect = User.DoesNotExist
        mock_create_edxapp_user.return_value = None, ""
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["test_1", "test_2"]
            },
            "redirect_uris": "http://testing-site.io/ http://testing-site.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application 4",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)
        self.assertFalse(Application.objects.filter(name=data["name"]).exists())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_called_once()
        mock_get_or_create_site.assert_called_once()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_with_wrong_user_data(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_or_create_site,
    ):
        """Tests the case where the user information
        is incomplete or has the wrong format in the
        request data.

        Expected behavior:
            - Status code 400 Bad Request.
        """
        message = b'{"user":{"username":["This field is required."]}}'
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "permissions": ["test_1", "test_2"]
            },
            "redirect_uris": "http://testing-site.io/ http://testing-site.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application 5",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(message, response.content)
        self.assertFalse(Application.objects.filter(name=data["name"]).exists())
        mock_get_edxapp_user.assert_not_called()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_not_called()

    @patch('eox_core.api.support.v1.views.get_or_create_site_from_oauth_app_uris')
    @patch('eox_core.api.support.v1.views.UserSignupSource')
    @patch('eox_core.api.support.v1.views.create_edxapp_user')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_create_oauth_application_without_sending_user_permissions(
        self,
        mock_get_edxapp_user,
        mock_create_edxapp_user,
        mock_get_user_signup_source,
        mock_get_or_create_site,
    ):
        """Tests the case where an Oauth Application is created
        without sending any permissions to assign to the user.

        Expected behavior:
            - The Oauth App is created.
            - Status code 200.
        """
        self.user.user_permissions.clear()
        mock_get_or_create_site.return_value = self.site
        mock_get_edxapp_user.return_value = self.user
        mock_get_user_signup_source.return_value = Mock()
        data = {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": [],
            },
            "redirect_uris": "http://testing-site6.io/ http://testing-site6.io",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application 6",
            "skip_authorization": True,
        }

        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(data["name"], response.data["name"])
        self.assertEqual(0, self.user.user_permissions.all().count())
        mock_get_edxapp_user.assert_called_once()
        mock_create_edxapp_user.assert_not_called()
        mock_get_or_create_site.assert_called_once()
