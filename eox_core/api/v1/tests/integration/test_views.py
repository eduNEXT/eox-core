"""
Integration test suite for the API v1 views.
"""

import requests
from django.http import HttpResponse
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_m_v1"
API_TIMEOUT = 5
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"


@override_settings(ALLOWED_HOSTS=["*"], SITE_ID=2)
class BaseAPIIntegrationTest(APITestCase):
    """
    Base class for the integration test suite.
    """

    def setUp(self):
        """
        Set up the test suite.
        """
        self.default_site = {
            "base_url": "http://local.edly.io",
            "domain": "local.edly.io",
        }
        self.tenant_x = {
            "base_url": "http://local.edly.io",
            "domain": "local.edly.io",
        }

    def get_access_token(self, tenant_base_url: str) -> str:
        """
        Get an access token for a tenant.

        Args:
            tenant_base_url (str): The tenant base URL.

        Returns:
            str: The access token.
        """
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        path = f"{tenant_base_url}/oauth2/access_token/"
        response = requests.post(path, data=data, timeout=API_TIMEOUT)
        return response.json()["access_token"]


@override_settings(EOX_CORE_USERS_BACKEND=EOX_CORE_USERS_BACKEND)
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
        access_token = self.get_access_token(tenant["base_url"])
        headers = {"Host": tenant["domain"], "Authorization": f"Bearer {access_token}"}
        path = f"{tenant['base_url']}{self.path}"
        response = requests.post(path, data=user_data, headers=headers, timeout=API_TIMEOUT)
        return response

    def get_user_in_tenant(self, tenant: dict, username: str) -> HttpResponse:
        """
        Get a user in a tenant.

        Args:
            tenant (dict): The tenant data.
            username (str): The username.

        Returns:
            HttpResponse: The response object.
        """
        access_token = self.get_access_token(tenant["base_url"])
        headers = {"Host": tenant["domain"], "Authorization": f"Bearer {access_token}"}
        path = f"{tenant['base_url']}{self.path}?username={username}"
        response = requests.get(path, headers=headers, timeout=API_TIMEOUT)
        return response

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

    def test_create_user_missing_required_fields(self):
        """
        Test creating a user in a tenant with invalid data.

        Open edX definitions tested:
        - `check_edxapp_account_conflicts`

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
        path = f"{self.default_site['base_url']}{self.path}"

        response = requests.get(path, timeout=API_TIMEOUT)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("version", response_data)
        self.assertIn("name", response_data)
        self.assertIn("git", response_data)
