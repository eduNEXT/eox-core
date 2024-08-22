"""
Integration test suite.

This suite performs multiple http requests to guarantee
that the Users API is behaving as expected on a live server.
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

try:
    from eox_tenant.models import Route, TenantConfig
except ImportError:
    Route = None
    TenantConfig = None
from oauth2_provider.models import Application
from rest_framework.status import HTTP_200_OK

CLIENT_ID = "apiclient"
CLIENT_SECRET = "apisecret"


def create_oauth_client(user: User, redirect_uris: list) -> None:
    """
    Create a new OAuth client.

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
        redirect_uris=redirect_uris,
    )


def create_admin_user() -> User:
    """
    Create a new admin user.

    Returns:
        User: The admin user.
    """
    return User.objects.create_superuser("eox-core-admin", "eox-core@mail.com", "p@$$w0rd")


def create_tenant(name: str, host: str) -> str:
    """
    Create a new tenant.

    Args:
        name (str): The tenant name.
        host (str): The tenant host.

    Returns:
        str: The tenant domain.
    """
    domain = f"{host}.local.edly.io"
    config = TenantConfig.objects.create(
        external_key=f"{host}-key",
        lms_configs={
            "EDNX_USE_SIGNAL": True,
            "PLATFORM_NAME": name,
            "SITE_NAME": domain,
            "course_org_filter": ["OpenedX"],
        },
    )
    Route.objects.create(domain=domain, config=config)
    Site.objects.create(domain=domain, name=name)
    return domain


@override_settings(ALLOWED_HOSTS=["*"], SITE_ID=2)
class TestUsersAPIIntegration(TestCase):
    """Integration test suite for the Users API"""

    def setUp(self):
        self.tenant_x_domain = create_tenant("Tenant X", "tenant-x")
        self.admin_user = create_admin_user()
        create_oauth_client(self.admin_user, redirect_uris=[f"http://{self.tenant_x_domain}/"])
        self.tenant_x_token = self.get_access_token(self.tenant_x_domain)

    def get_access_token(self, tenant_domain: str) -> str:
        """
        Get an access token for a tenant.

        Args:
            tenant_domain (str): The tenant domain.

        Returns:
            str: The access token.
        """
        access_token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        access_token_endpoint = f"http://{tenant_domain}/oauth2/access_token/"
        response_access_token = self.client.post(access_token_endpoint, data=access_token_data)
        return response_access_token.json()["access_token"]

    @override_settings(EOX_CORE_USERS_BACKEND="eox_core.edxapp_wrapper.backends.users_m_v1")
    def test_create_user_in_tenant(self):
        """Test the creation of a user in a tenant."""
        path = f"http://{self.tenant_x_domain}/eox-core/api/v1/user/"
        print(f'\n\nPath: {path}\n\n')
        data = {
            "username": "user-tenant-x",
            "email": "user@tenantx.com",
            "fullname": "User Tenant X",
            "password": "p@$$w0rd",
            "activate_user": True,
        }
        headers = {"Authorization": f"Bearer {self.tenant_x_token}", "Host": self.tenant_x_domain}

        response = self.client.post(path, data=data, headers=headers)

        response_data = response.json()
        print(f"\n\nResponse data: {response_data}\n\n")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["username"], data["username"])
        self.assertTrue(response_data["is_active"])
        self.assertFalse(response_data["is_staff"])
        self.assertFalse(response_data["is_superuser"])
