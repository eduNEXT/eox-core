"""Support API request mixin for the Pre Enrollments API."""

from __future__ import annotations

import ddt
import requests
from django.conf import settings as ds
from django.urls import reverse
from rest_framework import status

# TODO: move the FAKE_USER_DATA to a common place
from eox_core.api.v1.tests.integration.data.fake_users import FAKE_USER_DATA
from eox_core.api.v1.tests.integration.test_views import UsersAPIRequestMixin
from eox_core.tests.integration.utils import BaseIntegrationTest, make_request

settings = ds.INTEGRATION_TEST_SETTINGS


class SupportAPIRequestMixin:
    """Mixin class for the Pre Enrollments API request methods."""

    DELETE_USER_URL = f"{settings['EOX_CORE_API_BASE']}{reverse('eox-support-api:eox-support-api:edxapp-user')}"
    UPDATE_USERNAME_URL = (
        f"{settings['EOX_CORE_API_BASE']}{reverse('eox-support-api:eox-support-api:edxapp-replace-username')}"
    )
    OAUTH_APP_URL = (
        f"{settings['EOX_CORE_API_BASE']}{reverse('eox-support-api:eox-support-api:edxapp-oauth-application')}"
    )

    def delete_user(self, tenant: dict, params: dict | None = None) -> requests.Response:
        """
        Delete an edxapp user in a tenant.

        Args:
            tenant (dict): The tenant data.
            params (dict, optional): The query parameters for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "DELETE", url=self.DELETE_USER_URL, params=params)

    # TODO: Check of the default value of data should be None
    def update_username(self, tenant: dict, params: dict, data: dict | None = None) -> requests.Response:
        """
        Update an edxapp user's username in a tenant.

        Args:
            tenant (dict): The tenant data.
            params (dict): The query parameters for the request.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "PATCH", url=self.UPDATE_USERNAME_URL, params=params, data=data)

    # TODO: Check of the default value of data should be None
    def create_oauth_application(self, tenant: dict, data: dict | None = None) -> requests.Response:
        """
        Create an oauth application in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "POST", url=self.OAUTH_APP_URL, data=data)


@ddt.ddt
class TestEdxAppUserAPIIntegration(SupportAPIRequestMixin, BaseIntegrationTest, UsersAPIRequestMixin):
    """Integration tests for the EdxApp User API."""

    @ddt.data("username", "email")
    def test_delete_user_in_tenant_success(self, query_param: str) -> None:
        """
        Test delete an edxapp user in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `delete_edxapp_user`

        Expected result:
        - The status code is 200.
        - The response indicates the user was removed successfully from the tenant.
        - The user is not found in the tenant.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)

        response = self.delete_user(self.tenant_x, {query_param: data[query_param]})
        response_data = response.json()
        get_response = self.get_user(self.tenant_y, {query_param: data[query_param]})
        get_response_data = get_response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, f"The user {data['username']} <{data['email']}>  has been removed")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            get_response_data["detail"],
            f"No user found by {{'{query_param}': '{data[query_param]}'}} on site {self.tenant_y['domain']}.",
        )

    @ddt.data(
        ("username", "user-not-found"),
        ("email", "user-not-found@mail.com"),
    )
    @ddt.unpack
    def test_delete_user_in_tenant_not_found(self, query_param: str, value: str) -> None:
        """
        Test delete an edxapp user in a tenant that does not exist.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response indicates the user was not found in the tenant.
        """
        response = self.delete_user(self.tenant_x, {query_param: value})
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'{query_param}': '{value}'}} on site {self.tenant_x['domain']}.",
        )

    def test_delete_user_missing_required_fields(self) -> None:
        """
        Test delete an edxapp user in a tenant without providing the username or email.

        Expected result:
        - The status code is 400.
        - The response indicates the username is required.
        """
        response = self.delete_user(self.tenant_x)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, ["Email or username needed"])


@ddt.ddt
class TestOauthApplicationAPIIntegration(SupportAPIRequestMixin, BaseIntegrationTest, UsersAPIRequestMixin):
    """Integration tests for the Oauth Application API."""
