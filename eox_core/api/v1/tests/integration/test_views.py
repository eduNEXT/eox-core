"""
Integration test suite for the API v1 views.
"""

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_m_v1"


@override_settings(ALLOWED_HOSTS=["*"], SITE_ID=2)
class BaseAPIIntegrationTest(APITestCase):
    """
    Base class for the integration test suite.
    """

    def setUp(self):
        """
        Set up the test suite.
        """
        self.admin_user = self.create_admin_user()
        self.client.force_authenticate(user=self.admin_user)
        self.tenant_x = self.create_tenant("tenant-x")
        self.tenant_y = self.create_tenant("tenant-y")

    def create_admin_user(self) -> User:
        """
        Create a new admin user.

        Returns:
            User: The admin user.
        """
        return User.objects.create_superuser("eox-core-admin", "eox-core@mail.com", "p@$$w0rd")

    def create_tenant(self, tenant: str) -> dict:
        """
        Create a new tenant.

        Args:
            tenant (str): The tenant name.

        Returns:
            dict: The tenant data.
        """
        return {"domain": f"{tenant}.local.edly.io"}


class TestUsersAPIIntegration(BaseAPIIntegrationTest):
    """Integration test suite for the Users API"""

    def setUp(self):
        """Set up the test suite"""
        self.path = reverse("eox-core:eox-api:eox-api:edxapp-user")
        super().setUp()

    def create_user_in_tenant(self, tenant: dict, user_data: dict) -> HttpResponse:
        """
        Create a new user in a tenant.

        Args:
            tenant (dict): The tenant data.
            user_data (dict): The user data.

        Returns:
            HttpResponse: The response object.
        """
        headers = {"Host": tenant["domain"]}
        response = self.client.post(self.path, data=user_data, headers=headers)
        return response

    @override_settings(EOX_CORE_USERS_BACKEND=EOX_CORE_USERS_BACKEND)
    def test_create_user_in_tenant_success(self):
        """
        Test creating a user in a tenant.

        Open edX definitions tested:
        - `create_edxapp_user`
        - `check_edxapp_account_conflicts`

        Expected result:
        - The status code is 200.
        - The user is created successfully in the tenant with the provided data.
        """
        data = {
            "username": "user-tenant-x",
            "email": "user@tenantx.com",
            "fullname": "User Tenant X",
            "password": "p@$$w0rd",
            "activate_user": True,
        }

        response = self.create_user_in_tenant(self.tenant_x, data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["username"], data["username"])
        self.assertTrue(response_data["is_active"])
        self.assertFalse(response_data["is_staff"])
        self.assertFalse(response_data["is_superuser"])

    @override_settings(EOX_CORE_USERS_BACKEND=EOX_CORE_USERS_BACKEND)
    def test_create_user_missing_required_fields(self):
        """
        Test creating a user in a tenant with invalid data.

        Expected result:
            - The status code is 400.
            - The response contains the missing fields.
            - The user is not created in the tenant.
        """
        data = {
            "fullname": "User Tenant X",
            "password": "p@$$w0rd",
        }

        response = self.create_user_in_tenant(self.tenant_x, data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response_data)
        self.assertIn("username", response_data)


class TestInfoView(BaseAPIIntegrationTest):
    """
    Integration test suite for the info view.
    """

    def setUp(self):
        """
        Set up the test suite.
        """
        self.path = reverse("eox-core:eox-info")
        super().setUp()

    def test_info_view_success(self):
        """Test the info view.

        Expected result:
        - The status code is 200.
        - The response contains the version, name and git commit hash.
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("version", response_data)
        self.assertIn("name", response_data)
        self.assertIn("git", response_data)
