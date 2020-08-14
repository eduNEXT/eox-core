"""
Test module for users viewset.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient


class UsersUpdaterAPITest(TestCase):
    """Test class for users viewset."""

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """Setup method for test class."""
        self.user = User(username="test", email="test@example.com", password="testtest")
        self.client = APIClient()
        self.url = reverse("eox-api:eox-api:edxapp-user-updater")
        self.client.force_authenticate(user=self.user)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch('eox_core.api.v1.views.EdxappUserReadOnlySerializer')
    def test_update_success(self, user_serializer, get_edxapp_user, signup_source, _):
        """Used to test updating safe fields of an edxapp user."""
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        user_serializer.return_value.data = {}
        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_update_bad_sign_up_source(self, get_edxapp_user, signup_source, _):
        """Used to test that when an user has more than one signup source then the update can't be done."""
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 2

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with more than one sign up source."]}'
                         .encode())

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_update_role_not_allowed(self, get_edxapp_user, signup_source, _):
        """Used to test that if an user is staff or superuser then the update can't be done.ss"""
        user = User(username="test", email="test@example.com", password="testtest", is_staff=True)
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        get_edxapp_user.return_value = user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with roles like staff or superuser."]}'
                         .encode())
