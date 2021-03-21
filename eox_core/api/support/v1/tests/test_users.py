"""
Test module for users viewset.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient


class EdxappReplaceUsernameAPITest(TestCase):
    """Test class for update username APIView."""

    patch_permissions = patch('eox_core.api.support.v1.permissions.EoxCoreSupportAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """Setup method for test class."""
        self.user = User(username="test-username", email="test-username@example.com", password="testusername")
        self.client = APIClient()
        self.url = reverse("eox-support-api:eox-support-api:edxapp-replace-username")
        self.client.force_authenticate(user=self.user)

    @patch_permissions
    @patch('eox_core.api.support.v1.views.replace_username_cs_user')
    @patch('eox_core.api.support.v1.serializers.UserSignupSource')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    @patch('eox_core.api.support.v1.views.EdxappUserReadOnlySerializer')
    def test_replace_username_success(self, user_serializer, get_edxapp_user, signup_source, replace_username_cs_user, _):
        """Test the replacement of the username of an edxapp user."""
        update_data = {
            "username": self.user.username,
            "new_username": "replaced-username",
        }

        user_serializer.return_value.data = {}
        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual("replaced-username", self.user.username)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @patch_permissions
    @patch('eox_core.api.support.v1.serializers.UserSignupSource')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_replace_username_bad_sign_up_source(self, get_edxapp_user, signup_source, _):
        """
        Tests that when a user has more than one signup source then the
        username cannot be replaced.
        """
        update_data = {
            "username": self.user.username,
            "new_username": "another-username",
        }

        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 2

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with more than one sign up source."]}'
                         .encode())

    @patch_permissions
    @patch('eox_core.api.support.v1.serializers.UserSignupSource')
    @patch('eox_core.api.support.v1.views.get_edxapp_user')
    def test_replace_username_staff_user(self, get_edxapp_user, signup_source, _):
        """Tests that if a user is staff or superuser then the username cannot be replaced."""
        user = User(username="test", email="test@example.com", password="testtest", is_staff=True)
        update_data = {
            "username": user.username,
            "new_username": "new-test-username",
        }

        get_edxapp_user.return_value = user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with roles like staff or superuser."]}'
                         .encode())
