"""
Integration test suite for the API v1 views.
"""

# pylint: disable=too-many-lines
from __future__ import annotations

import ddt
import requests
from django.conf import settings as ds
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from eox_core.api.v1.tests.integration.data.fake_users import FAKE_USER_DATA

settings = ds.INTEGRATION_TEST_SETTINGS

USER_URL = f"{settings['EOX_CORE_API_BASE']}{reverse('eox-api:eox-api:edxapp-user')}"
USER_UPDATER_URL = f"{settings['EOX_CORE_API_BASE']}{reverse('eox-api:eox-api:edxapp-user-updater')}"
ENROLLMENT_URL = f"{settings['EOX_CORE_API_BASE']}{reverse('eox-api:eox-api:edxapp-enrollment')}"


def get_access_token(tenant_base_url: str) -> str:
    """
    Get an access token for a tenant.

    Args:
        tenant_base_url (str): The tenant base URL.

    Returns:
        str: The access token.
    """
    data = {
        "client_id": settings["CLIENT_ID"],
        "client_secret": settings["CLIENT_SECRET"],
        "grant_type": "client_credentials",
    }
    url = f"{tenant_base_url}/oauth2/access_token/"
    response = requests.post(url, data=data, timeout=settings["API_TIMEOUT"])
    return response.json()["access_token"]


# pylint: disable=too-many-arguments
def make_request(
    tenant: dict,
    method: str,
    url: str,
    json: dict | None = None,
    data: dict | None = None,
    params: dict | None = None,
    with_auth: bool = True,
) -> requests.Response:
    """
    Make a request to a site (default site or tenant).

    Args:
        tenant (dict): The tenant data.
        method (str): The HTTP method ('GET', 'POST', etc.).
        url (str): The URL to make the request to.
        json (dict, optional): The JSON data for POST, PATCH and PUT requests.
        data (dict, optional): The data for POST, PATCH and PUT requests.
        params (dict, optional): The parameters for GET and DELETE requests.
        with_auth (bool, optional): Whether to include the access token in the request headers.

    Returns:
        requests.Response: The response object.
    """
    headers = {"Host": tenant["domain"]}
    if with_auth:
        access_token = get_access_token(tenant["base_url"])
        headers["Authorization"] = f"Bearer {access_token}"
    full_url = f"{tenant['base_url']}/{url}"

    method = method.upper()
    if method not in ("GET", "POST", "PATCH", "PUT", "DELETE"):
        raise ValueError(f"Unsupported HTTP method: {method}.")

    return requests.request(
        method,
        full_url,
        json=json,
        data=data,
        params=params,
        headers=headers,
        timeout=settings["API_TIMEOUT"],
    )


class BaseAPIIntegrationTest(TestCase):
    """
    Base class for the integration test suite.
    """

    def setUp(self):
        """
        Set up the test suite.
        """
        self.default_site = self.get_tenant_data()
        self.tenant_x = self.get_tenant_data("tenant-x")
        self.tenant_y = self.get_tenant_data("tenant-y")

    def get_tenant_data(self, prefix: str = "") -> dict:
        """
        Get the tenant data.

        If no prefix is provided, the default site data is returned.

        Args:
            prefix (str, optional): The tenant prefix. Defaults to "".

        Returns:
            dict: The tenant data.
        """
        domain = f"{prefix}.{settings['LMS_BASE']}" if prefix else settings["LMS_BASE"]
        return {
            "base_url": f"http://{domain}",
            "domain": domain,
        }


class UsersAPIRequestMixin:
    """
    Mixin class for the API request methods.
    """

    def create_user(self, tenant: dict, data: dict) -> requests.Response:
        """
        Create a new user in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict): The user data.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "POST", url=USER_URL, json=data)

    def get_user(self, tenant: dict, params: dict | None = None) -> requests.Response:
        """
        Get a user in a tenant by username or email.

        Args:
            tenant (dict): The tenant data.
            params (dict, optional): The query parameters for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "GET", url=USER_URL, params=params)

    def update_user(self, tenant: dict, data: dict) -> requests.Response:
        """
        Update a user in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict): The user data.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "PATCH", url=USER_UPDATER_URL, json=data)


class EnrollmentAPIRequestMixin:
    """Mixin class for the API request methods."""

    def create_enrollment(self, tenant: dict, data: dict) -> requests.Response:
        """
        Create a new user in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict): The user data.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "POST", url=ENROLLMENT_URL, data=data)

    def get_enrollment(self, tenant: dict, data: dict | None = None) -> requests.Response:
        """
        Get a user in a tenant by username or email.

        Args:
            tenant (dict): The tenant data.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "GET", url=ENROLLMENT_URL, data=data)

    def update_enrollment(self, tenant: dict, data: dict | None = None) -> requests.Response:
        """
        Update an enrollment in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "PUT", url=ENROLLMENT_URL, data=data)

    def delete_enrollment(self, tenant: dict, data: dict | None = None) -> requests.Response:
        """
        Delete an enrollment in a tenant.

        Args:
            tenant (dict): The tenant data.
            data (dict, optional): The body data for the request.

        Returns:
            requests.Response: The response object.
        """
        return make_request(tenant, "DELETE", url=ENROLLMENT_URL, data=data)


@ddt.ddt
class TestUsersAPIIntegration(BaseAPIIntegrationTest, UsersAPIRequestMixin):
    """Integration test suite for the Users API"""

    @ddt.data(
        {"is_staff": False, "is_superuser": False},
        {"is_staff": True, "is_superuser": False},
        {"is_staff": False, "is_superuser": True},
        {"is_staff": True, "is_superuser": True},
    )
    def test_create_user_in_tenant_success(self, permissions: dict) -> None:
        """
        Test creating a user in a tenant.

        Open edX definitions tested:
        - `create_edxapp_user`
        - `check_edxapp_account_conflicts`

        Expected result:
        - The status code is 200.
        - The user is created successfully in the tenant with the provided data.
        """
        data = next(FAKE_USER_DATA)
        data.update(permissions)

        response = self.create_user(self.tenant_x, data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["username"], data["username"])
        self.assertTrue(response_data["is_active"])
        self.assertFalse(response_data["is_staff"])
        self.assertFalse(response_data["is_superuser"])

    def test_create_user_missing_required_fields(self) -> None:
        """
        Test creating a user in a tenant with invalid data.

        Open edX definitions tested:
        - `check_edxapp_account_conflicts`

        Expected result:
        - The status code is 400.
        - The response contains the missing fields.
        - The user is not created in the tenant.
        """
        data = next(FAKE_USER_DATA)
        del data["email"]
        del data["username"]

        response = self.create_user(self.tenant_x, data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response_data)
        self.assertIn("username", response_data)

    def test_create_user_in_tenant_user_already_exists(self) -> None:
        """
        Test creating a user in a tenant that already exists.

        Open edX definitions tested:
        - `check_edxapp_account_conflicts`

        Expected result:
        - The status code is 400.
        - The response contains an error message.
        - The user is not created in the tenant.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)

        response = self.create_user(self.tenant_x, data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_data)

    @ddt.data("username", "email")
    def test_get_user_in_tenant_success(self, query_param: str) -> None:
        """
        Test getting a user in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 200.
        - The response contains the user data.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)

        response = self.get_user(self.tenant_x, {query_param: data[query_param]})

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data[query_param], data[query_param])

    def test_get_user_of_another_tenant(self) -> None:
        """
        Test getting a user that belongs to another tenant.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response contains an error message.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)

        response = self.get_user(self.tenant_y, {"username": data["username"]})

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'username': '{data['username']}'}} on site {self.tenant_y['domain']}.",
        )

    @ddt.data(
        ("username", "user-not-found"),
        ("email", "user-not-found@mail.com"),
    )
    @ddt.unpack
    def test_get_user_in_tenant_user_not_found(self, param: str, value: str) -> None:
        """
        Test getting a user in a tenant that does not exist.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response contains an error message.
        """
        response = self.get_user(self.tenant_x, {param: value})

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'{param}': '{value}'}} on site {self.tenant_x['domain']}.",
        )

    def test_update_user_in_tenant_success(self) -> None:
        """
        Test updating a user in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `get_user_profile`
        - `check_edxapp_account_conflicts`
        - `get_user_read_only_serializer`

        Expected result:
        - The status code is 200.
        - The user is updated successfully in the tenant with the provided data.
        """
        data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, data)
        updated_data = next(FAKE_USER_DATA)
        updated_data["username"] = data["username"]
        updated_data["email"] = data["email"]

        response = self.update_user(self.tenant_x, data=updated_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], data["username"])
        self.assertEqual(response_data["email"], data["email"])
        self.assertEqual(response_data["name"], updated_data["fullname"])
        self.assertEqual(response_data["mailing_address"], updated_data["mailing_address"])
        self.assertEqual(response_data["year_of_birth"], updated_data["year_of_birth"])
        self.assertEqual(response_data["gender"], updated_data["gender"])
        self.assertEqual(response_data["level_of_education"], updated_data["level_of_education"])
        self.assertEqual(response_data["goals"], updated_data["goals"])
        self.assertTrue(response_data["is_active"])

    @ddt.data(
        ("username", "user-not-found"),
        ("email", "user-not-found@mail.com"),
    )
    @ddt.unpack
    def test_update_user_in_tenant_user_not_found(self, param: str, value: str) -> None:
        """
        Test updating a user in a tenant that does not exist.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response contains an error message.
        """
        response = self.update_user(self.tenant_x, {param: value})

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'{param}': '{value}'}} on site {self.tenant_x['domain']}.",
        )


@ddt.ddt
class TestEnrollmentAPIIntegration(BaseAPIIntegrationTest, UsersAPIRequestMixin, EnrollmentAPIRequestMixin):
    """Integration test suite for the Enrollment API"""

    def setUp(self) -> None:
        """Set up the test suite"""
        self.course_id = settings["COURSE_ID"]
        self.mode = "audit"
        super().setUp()

    @ddt.data("email", "username")
    def test_create_enrollment_success(self, param: str) -> None:
        """
        Test creating a enrollment with a valid user, course and mode in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `create_enrollment`
        - `check_edxapp_account_conflicts`
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 200.
        - The enrollment is created successfully in the tenant with the provided data.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], user_data["username"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertTrue(response_data["is_active"])
        self.assertIn("created", response_data)

    @ddt.data(
        ("mode", {"mode": ["This field is required."]}),
        ("course_id", {"non_field_errors": ["You have to provide a course_id or bundle_id"]}),
        ("username", {"non_field_errors": ["Email or username needed"]}),
    )
    @ddt.unpack
    def test_create_enrollment_missing_required_fields(self, param: str, error: list | dict) -> None:
        """
        Test creating a enrollment with missing required fields.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 400.
        - The response contains a message about the missing field.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            "username": user_data["username"],
            "mode": self.mode,
            "course_id": self.course_id,
        }
        enrollment_data.pop(param)

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data, error)

    @ddt.data("email", "username")
    def test_force_create_enrollment_success(self, param: str) -> None:
        """
        Test force creating a enrollment with a valid user, course and mode in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `create_enrollment`
        - `check_edxapp_account_conflicts`
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 200.
        - The enrollment is created successfully in the tenant with the provided data.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
            "force": True,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], user_data["username"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertTrue(response_data["is_active"])
        self.assertIn("created", response_data)

    @ddt.data("email", "username")
    def test_create_valid_course_mode_invalid_user(self, param: str) -> None:
        """
        Test creating a enrollment with a valid course, valid mode, and a non-existent user in a tenant.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 400.
        - The response contains an error message about the user not found.
        - The enrollment is not created in the tenant.
        """
        enrollment_data = {
            param: param,
            "course_id": self.course_id,
            "mode": self.mode,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_data)
        self.assertEqual(response_data["non_field_errors"], ["User not found"])

    @ddt.data("email", "username")
    def test_create_valid_course_mode_invalid_user_for_tenant(self, param: str) -> None:
        """
        Test creating a enrollment with a valid course, valid mode, and a user from another tenant.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 202.
        - The response contains an error message about the user not found on the tenant.
        - The enrollment is not created in the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_y, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response_data["error"]["detail"],
            f"No user found by {{'{param}': '{enrollment_data[param]}'}} on site {self.tenant_x['domain']}.",
        )

    @ddt.data("email", "username")
    def test_create_valid_user_mode_invalid_course(self, param: str) -> None:
        """
        Test creating a enrollment with a valid user, valid mode, and a non-existent course in a tenant.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 400.
        - The response contains an error message about the course not found.
        - The enrollment is not created in the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": "course-v1:OpenedX+DemoX+NonExistentCourse",
            "mode": self.mode,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_data)
        self.assertEqual(response_data["non_field_errors"], ["Course not found"])

    @ddt.data("email", "username")
    def test_create_valid_user_mode_invalid_course_for_tenant(self, param: str) -> None:
        """
        Test creating a enrollment with a valid user, valid mode, and a course from another tenant.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`
        - `validate_org`

        Expected result:
        - The status code is 400.
        - The response contains an error message about the course not found on the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_y, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }

        response = self.create_enrollment(self.tenant_y, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course_id", response_data)
        self.assertEqual(response_data["course_id"], [f"Invalid course_id {self.course_id}"])

    @ddt.data("email", "username")
    def test_create_valid_user_course_invalid_mode(self, param: str) -> None:
        """
        Test creating a enrollment with a valid user, valid course, and a not available mode in a tenant.

        Open edX definitions tested:
        - `check_edxapp_enrollment_is_valid`
        - `api.validate_course_mode`

        Expected result:
        - The status code is 400.
        - The response contains an error message about the mode not found.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": "masters",
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_data)
        self.assertEqual(response_data["non_field_errors"], ["Mode not found"])

    @ddt.data("email", "username")
    def test_force_create_valid_user_course_mode_not_allowed(self, param: str) -> None:
        """
        Test creating a enrollment with a valid user, valid course, and a not available mode in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `create_enrollment`
        - `check_edxapp_account_conflicts`
        - `check_edxapp_enrollment_is_valid`

        Expected result:
        - The status code is 200.
        - The enrollment is created successfully in the tenant with the provided data.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": "masters",
            "force": True,
        }

        response = self.create_enrollment(self.tenant_x, enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], user_data["username"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertTrue(response_data["is_active"])
        self.assertIn("created", response_data)

    @ddt.data("email", "username")
    def test_get_enrollment_success(self, param: str) -> None:
        """
        Test getting a enrollment with a valid user, course and mode in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `get_enrollment`

        Expected result:
        - The status code is 200.
        - The response contains the enrollment data.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)

        response = self.get_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], user_data["username"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertTrue(response_data["is_active"])
        self.assertIn("created", response_data)

    @ddt.data("email", "username")
    def test_get_enrollment_does_not_exist(self, param: str) -> None:
        """
        Test getting a enrollment that does not exist in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `get_enrollment`

        Expected result:
        - The status code is 404.
        - The response contains an error message about the enrollment not found.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
        }

        response = self.get_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_data, [f"No enrollment found for user:`{user_data['username']}`"])

    @ddt.data("email", "username")
    def test_get_enrollment_not_found_in_tenant(self, param: str) -> None:
        """
        Test getting a enrollment that belongs to another tenant.

        Open edX definitions tested:
        - `get_edxapp_user`

        Expected result:
        - The status code is 404.
        - The response contains an error message about the user not found on the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)

        response = self.get_enrollment(self.tenant_y, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'{param}': '{user_data[param]}'}} on site {self.tenant_y['domain']}.",
        )

    @ddt.data("email", "username")
    def test_delete_enrollment_success(self, param: str) -> None:
        """
        Test deleting a enrollment with a valid user, course and mode in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `delete_enrollment`

        Expected result:
        - The status code is 204.
        - The enrollment is deleted successfully in the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)

        response = self.delete_enrollment(self.tenant_x, data=enrollment_data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @ddt.data("email", "username")
    def test_delete_enrollment_does_not_exist(self, param: str) -> None:
        """
        Test deleting a enrollment that does not exist in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `delete_enrollment`

        Expected result:
        - The status code is 404.
        - The response contains an error message about the enrollment not found.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
        }

        response = self.delete_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No enrollment found for user: `{user_data['username']}` on course_id `{self.course_id}`",
        )

    @ddt.data("email", "username")
    def test_delete_invalid_enrollment_for_tenant(self, param: str) -> None:
        """
        Test deleting a enrollment that belongs to another tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `delete_enrollment`

        Expected result:
        - The status code is 404.
        - The response contains an error message about the user not found on the tenant.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)

        response = self.delete_enrollment(self.tenant_y, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_data)
        self.assertEqual(
            response_data["detail"],
            f"No user found by {{'{param}': '{user_data[param]}'}} on site {self.tenant_y['domain']}.",
        )

    @ddt.data("email", "username")
    def test_update_valid_enrollment_change_is_active_mode_field(self, param: str) -> None:
        """
        Test updating an existing enrollment. Update is_active and mode field.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `update_enrollment`

        Expected result:
        - The status code is 200.
        - The enrollment is updated successfully in the tenant with the provided data.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "is_active": False,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)
        enrollment_data["is_active"] = True
        enrollment_data["mode"] = "honor"

        response = self.update_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["user"], user_data["username"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertTrue(response_data["is_active"])

    @ddt.data("email", "username")
    def test_update_valid_enrollment_update_invalid_mode(self, param: str) -> None:
        """
        Test updating an existing enrollment. Update to invalid mode.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `update_enrollment`

        Expected result:
        - The status code is 400.
        - The response contains an error message about the mode not found.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "is_active": True,
            "mode": self.mode,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)
        enrollment_data["mode"] = "masters"

        response = self.update_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response_data)
        self.assertEqual(response_data["non_field_errors"], ["Mode not found"])

    @ddt.data("email", "username")
    def test_update_enrollment_does_not_exist(self, param: str) -> None:
        """
        Test updating an enrollment that does not exist in a tenant.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `update_enrollment`

        Expected result:
        - The status code is 202.
        - The response contains an error message about the enrollment not found.
        """
        user_data = next(FAKE_USER_DATA)
        self.create_user(self.tenant_x, user_data)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "is_active": False,
            "mode": "honor",
        }

        response = self.update_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response_data["error"]["detail"], f"No enrollment found for {user_data['username']}")

    @ddt.data("email", "username")
    def test_update_valid_enrollment_force_post(self, param: str) -> None:
        """
        Test updating an existing enrollment. Update is_active and mode field with force mode.

        Open edX definitions tested:
        - `get_edxapp_user`
        - `update_enrollment`

        Expected result:
        - The status code is 200.
        - The enrollment is updated successfully in the tenant with the provided data.
        """
        user_data = next(FAKE_USER_DATA)
        enrollment_data = {
            param: user_data[param],
            "course_id": self.course_id,
            "is_active": False,
            "mode": self.mode,
            "force": True,
        }
        self.create_user(self.tenant_x, user_data)
        self.create_enrollment(self.tenant_x, enrollment_data)
        enrollment_data["is_active"] = True
        enrollment_data["mode"] = "honor"

        response = self.create_enrollment(self.tenant_x, data=enrollment_data)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["username"], user_data["username"])
        self.assertEqual(response_data["course_id"], enrollment_data["course_id"])
        self.assertEqual(response_data["mode"], enrollment_data["mode"])
        self.assertTrue(response_data["is_active"])


class TestInfoView(BaseAPIIntegrationTest):
    """
    Integration test suite for the info view.
    """

    def setUp(self):
        """
        Set up the test suite.
        """
        self.url = f"{settings['EOX_CORE_API_BASE']}{reverse('eox-info')}"
        super().setUp()

    def test_info_view_success(self) -> None:
        """Test the info view.

        Expected result:
        - The status code is 200.
        - The response contains the version, name and git commit hash.
        """
        response = make_request(self.default_site, "GET", url=self.url, with_auth=False)

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("version", response_data)
        self.assertIn("name", response_data)
        self.assertIn("git", response_data)
