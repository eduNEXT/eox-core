"""
Integration test suite.

This suite performs multiple http requests to guarantee
that the Grade API is behaving as expected on a live server.
"""

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from eox_tenant.models import Route, TenantConfig
from oauth2_provider.models import Application

CLIENT_ID = "apiclient"
CLIENT_SECRET = "apisecret"


def create_oauth_client(user: User):
    """
    Create a new OAuth client.
    """
    return Application.objects.create(
        name="eox-core-app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        user=user,
    )


def create_admin_user():
    """
    Create a new admin user.
    """
    return User.objects.create_superuser("eox-core-admin")


def create_tenant(name: str, host: str):
    """
    Create a new tenant.
    """
    domain = f"{host}.local.edly.io"
    config = TenantConfig.objects.create(
        external_key=f"{host}-key",
        lms_configs={
            "EDNX_USE_SIGNAL": True,
            "PLATFORM_NAME": name,
            "SITE_NAME": f"{domain}:8000",
            "course_org_filter": ["OpenedX"],
        },
    )
    Route.objects.create(domain=domain, config=config)
    Site.objects.create(domain=f"{domain}:8000", name=name)
    return domain


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    SITE_ID=2,
    EOX_CORE_USERS_BACKEND="eox_core.edxapp_wrapper.backends.users_m_v1",
)
class TestUserIntegration(TestCase):
    """Integration test suite for the Users API"""

    def setUp(self):
        self.grade_endpoint = "eox-core/api/v1/grade/"
        admin_user = create_admin_user()
        create_oauth_client(admin_user)
        self.tenant_x_domain = create_tenant("Tenant X", "tenant-x")
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

    def test_create_user_in_tenant(self):
        """
        Create a new user in a tenant.
        """
        create_user_endpoint = f"http://{self.tenant_x_domain}/eox-core/api/v1/user/"
        payload = {
            "username": "user-tenant-x",
            "email": "user@tenantx.com",
            "fullname": "User Tenant X",
            "password": "p@$$w0rd",
            "activate_user": True,
        }
        headers = {"Authorization": f"Bearer {self.tenant_x_token}"}
        response = self.client.post(create_user_endpoint, data=payload, headers=headers)

        self.assertEqual(response.status_code, 200)
