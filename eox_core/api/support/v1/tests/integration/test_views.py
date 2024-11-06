"""Support API integration tests."""

from __future__ import annotations

import ddt
import requests
from django.conf import settings as ds
from django.urls import reverse
from rest_framework import status

from eox_core.api.v1.tests.integration.test_views import UsersAPIRequestMixin
from eox_core.tests.integration.data.fake_users import FAKE_USER_DATA
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

    def update_username(self, tenant: dict, params: dict | None = None, data: dict | None = None) -> requests.Response:
        """
        Update an edxapp user's username in a tenant.

        Args:
            tenant (dict): The tenant data.
            params (dict, optional): The query parameters for the request.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "PATCH", url=self.UPDATE_USERNAME_URL, params=params, data=data)

    def create_oauth_application(self, tenant: dict, data: dict | None = None) -> requests.Response:
        """
        Create an oauth application in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "POST", url=self.OAUTH_APP_URL, json=data)


@ddt.ddt
class TestEdxAppUserAPIIntegration(
    SupportAPIRequestMixin,
    BaseIntegrationTest,
    UsersAPIRequestMixin,
):
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
        get_response = self.get_user(self.tenant_x, {"email": data["email"]})
        get_response_data = get_response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, f"The user {data['username']} <{data['email']}>  has been removed")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            get_response_data,
            {"detail": f"No user found by {{'email': '{data['email']}'}} on site {self.tenant_x['domain']}."},
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
        - The response indicates the username or email is required.
        """
        response = self.delete_user(self.tenant_x)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, ["Email or username needed"])

    @ddt.data("username", "email")
    def test_update_username_in_tenant_success(self, query_param: str) -> None:
        """
        Test update an edxapp user's username in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `check_edxapp_account_conflicts`
        - `replace_username_cs_user`
        - `get_user_read_only_serializer`

        Expected result:
        - The status code is 200.
        - The response indicates the username was updated successfully.
        - The user is found in the tenant with the new username.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)
        new_username = f"new-username-{query_param}"

        response = self.update_username(self.tenant_x, {query_param: data[query_param]}, {"new_username": new_username})
        response_data = response.json()
        get_response = self.get_user(self.tenant_x, {"username": new_username})
        get_response_data = get_response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], new_username)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["username"], new_username)

    def test_update_username_in_tenant_not_found(self) -> None:
        """
        Test update an edxapp user's username in a tenant that does not exist.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response indicates the user was not found in the tenant.
        """
        response = self.update_username(
            self.tenant_x,
            {"username": "user-not-found"},
            {"new_username": "new-username"},
        )
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'username': 'user-not-found'}} on site {self.tenant_x['domain']}.",
        )

    def test_update_username_in_tenant_missing_params(self) -> None:
        """
        Test update an edxapp user's username in a tenant without providing the username.

        Expected result:
        - The status code is 400.
        - The response indicates the username is required.
        """
        response = self.update_username(self.tenant_x)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, ["Email or username needed"])

    def test_update_username_in_tenant_missing_body(self) -> None:
        """
        Test update an edxapp user's username in a tenant without providing the new username.

        Expected result:
        - The status code is 400.
        - The response indicates the new username is required.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)

        response = self.update_username(self.tenant_x, params={"username": data["username"]})
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, {"new_username": ["This field is required."]})


@ddt.ddt
class TestOauthApplicationAPIIntegration(SupportAPIRequestMixin, BaseIntegrationTest, UsersAPIRequestMixin):
    """Integration tests for the Oauth Application API."""

    @ddt.data(True, False)
    def test_create_oauth_application_in_tenant_success(self, create_user: bool) -> None:
        """
        Test create an oauth application in a tenant. The user is created if it does not exist.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `create_edxapp_user`
        - `UserSignupSource`

        Expected result:
        - The status code is 200.
        - The response indicates the oauth application was created successfully.
        """
        user_data = next(FAKE_USER_DATA)
        if create_user:
            self.create_user(self.tenant_x, user_data)
        data = {
            "user": {
                "fullname": user_data["fullname"],
                "email": user_data["email"],
                "username": user_data["username"],
                "permissions": ["can_call_eox_core", "can_call_eox_tenant"],
            },
            "redirect_uris": f"http://{self.tenant_x['domain']}/",
            "client_type": "confidential",
            "authorization_grant_type": "client-credentials",
            "name": "test-application",
            "skip_authorization": True,
        }

        response = self.create_oauth_application(self.tenant_x, data)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["user"], {"email": user_data["email"], "username": user_data["username"]})
        self.assertEqual(response_data["redirect_uris"], f"http://{self.tenant_x['domain']}/")
        self.assertEqual(response_data["client_type"], data["client_type"])
        self.assertEqual(response_data["authorization_grant_type"], data["authorization_grant_type"])
        self.assertEqual(response_data["name"], data["name"])
        self.assertEqual(response_data["skip_authorization"], data["skip_authorization"])

    def test_create_oauth_application_in_tenant_missing_required_fields(self) -> None:
        """
        Test create an oauth application in a tenant without providing the required fields.

        Expected result:
        - The status code is 400.
        - The response indicates the required fields are missing.
        """
        response = self.create_oauth_application(self.tenant_x)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_data,
            {
                "user": ["This field is required."],
                "client_type": ["This field is required."],
                "authorization_grant_type": ["This field is required."],
            },
        )
