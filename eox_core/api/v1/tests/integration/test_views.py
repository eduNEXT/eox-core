"""
Integration test suite for the API v1 views.
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse

try:
    from eox_tenant.models import Route, TenantConfig
except ImportError:
    Route = None
    TenantConfig = None
from oauth2_provider.models import Application
from rest_framework import status

CLIENT_ID = "apiclient"
CLIENT_SECRET = "apisecret"
EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_m_v1"


def create_oauth2_client(user: User) -> None:
    """
    Create a new OAuth2 client.

    Args:
        user (User): The user that will own the client.
    """
    Application.objects.create(
        name="eox-core-app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        user=user,
    )


def create_admin_user() -> User:
    """
    Create a new admin user.

    Returns:
        User: The admin user.
    """
    return User.objects.create_superuser("eox-core-admin", "eox-core@mail.com", "p@$$w0rd")


@override_settings(ALLOWED_HOSTS=["*"], SITE_ID=2)
class TestUsersAPIIntegration(TestCase):
    """Integration test suite for the Users API"""

    def setUp(self):
        """Set up the test suite"""
        self.path = reverse("eox-core:eox-api:eox-api:edxapp-user")
        self.admin_user = create_admin_user()
        create_oauth2_client(self.admin_user)
        self.tenant_x = self.create_tenant("tenant-x")
        self.tenant_y = self.create_tenant("tenant-y")

    @override_settings(EOX_CORE_USERS_BACKEND=EOX_CORE_USERS_BACKEND)
    def create_tenant(self, tenant: str) -> dict:
        """
        Create a new tenant.

        Args:
            tenant (str): The tenant name.

        Returns:
            dict: The tenant data.
        """
        domain = f"{tenant}.local.edly.io"
        name = tenant.capitalize()
        config = TenantConfig.objects.create(
            external_key=f"{domain}-key",
            lms_configs={
                "EDNX_USE_SIGNAL": True,
                "PLATFORM_NAME": name,
                "SITE_NAME": domain,
                "course_org_filter": ["OpenedX"],
            },
        )
        Route.objects.create(domain=domain, config=config)  # pylint: disable=no-member
        Site.objects.create(domain=domain, name=name)
        return {"domain": domain, "token": self.get_access_token(domain)}

    def get_access_token(self, tenant_domain: str) -> str:
        """
        Get an access token for a tenant.

        Args:
            tenant_domain (str): The tenant domain.

        Returns:
            str: The access token.
        """
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        headers = {"Host": tenant_domain}
        path = f"http://{tenant_domain}/oauth2/access_token/"
        response = self.client.post(path, data=data, headers=headers)
        return response.json()["access_token"]

    def create_user_in_tenant(self, tenant: dict, user_data: dict) -> HttpResponse:
        """
        Create a new user in a tenant.

        Args:
            tenant (dict): The tenant data.
            user_data (dict): The user data.

        Returns:
            HttpResponse: The response object.
        """
        headers = {"Authorization": f"Bearer {tenant['token']}", "Host": tenant["domain"]}
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


@override_settings(ALLOWED_HOSTS=["testserver"], SITE_ID=2)
class TestInfoView(TestCase):
    """
    Integration test suite for the info view.
    """

    def setUp(self):
        """
        Set up the base URL for the tests
        """
        self.path = reverse("eox-core:eox-info")

    def test_info_view(self):
        """
        Tests the info view endpoint in Tutor
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("version", response_data)
        self.assertIn("name", response_data)
        self.assertIn("git", response_data)
