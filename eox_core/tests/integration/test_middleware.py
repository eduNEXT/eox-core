"""Test Middlewares for the EOX Core."""

import ddt
import requests
from django.conf import settings as ds
from rest_framework import status

from eox_core.tests.integration.utils import BaseIntegrationTest

settings = ds.INTEGRATION_TEST_SETTINGS


@ddt.ddt
class TestPathRedirectionMiddleware(BaseIntegrationTest):
    """Integration tests for the PathRedirectionMiddleware."""

    def __init__(self, *args, **kwargs):
        """Initialize the class attributes."""
        super().__init__(*args, **kwargs)
        self.tenant_x_url = self.tenant_x.get("base_url")

    def get_session(self) -> requests.Session:
        """
        Start and returns a session to authenticate with the Open edX platform.

        Returns:
            requests.Session: The session object.
        """
        session = requests.Session()
        session.get(self.tenant_x_url)
        csrf_token = session.cookies.get("csrftoken")

        login_url = f"{self.tenant_x_url}/api/user/v2/account/login_session/"
        login_data = {
            "email_or_username": settings["SESSION_USER_USERNAME"],
            "password": settings["SESSION_USER_PASSWORD"],
        }
        headers = {
            "X-CSRFToken": csrf_token,
            "Referer": self.tenant_x_url,
        }

        session.post(login_url, data=login_data, headers=headers)

        return session

    def get_request(self, url: str, with_session: bool) -> requests.Response:
        """
        Make a GET request to the given URL.

        Args:
            url (str): The URL to make the request to.
            with_session (bool): Whether to use the session or not.

        Returns:
            requests.Response: The response object.
        """
        request_method = self.get_session().get if with_session else requests.get
        return request_method(url, timeout=settings["API_TIMEOUT"])

    @ddt.data(False, True)
    def test_without_redirect(self, with_session: bool) -> None:
        """
        Test the PathRedirectionMiddleware without any redirection.

        The `/about` path is not defined in the configuration.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 200.
        - The URL is the same as the requested URL.
        """
        response = self.get_request(f"{self.tenant_x_url}/about", with_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/about")

    @ddt.data(False, True)
    def test_redirect_always(self, with_session: bool) -> None:
        """
        Test the `redirect_always` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The history contains a 302 status code.
        - The status code is 200.
        - The URL is the configured redirect URL.
        """
        response = self.get_request(f"{self.tenant_x_url}/blog", with_session)

        self.assertEqual(response.history[0].status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/donate")

    @ddt.data(False, True)
    def test_login_required(self, with_session: bool) -> None:
        """
        Test the `login_required` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 200.
        - If the user is not logged in, the URL is the login page.
        - If the user is logged in, the URL is the requested URL.
        """
        final_path = "tos" if with_session else "login?next=/tos"

        response = self.get_request(f"{self.tenant_x_url}/tos", with_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/{final_path}")

    @ddt.data(False, True)
    def test_not_found(self, with_session: bool) -> None:
        """
        Test the `not_found` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 404.
        - The URL is the same as the requested URL.
        """
        response = self.get_request(f"{self.tenant_x_url}/privacy", with_session)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.url, f"{self.tenant_x_url}/privacy")

    @ddt.data(False, True)
    def test_not_found_loggedin(self, with_session: bool) -> None:
        """
        Test the `not_found_loggedin` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - If the user is logged in, the status code is 404.
        - If the user is not logged in, the status code is 200.
        """
        status_code = status.HTTP_404_NOT_FOUND if with_session else status.HTTP_200_OK

        response = self.get_request(f"{self.tenant_x_url}/help", with_session)

        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.url, f"{self.tenant_x_url}/help")

    @ddt.data(False, True)
    def test_not_found_loggedout(self, with_session: bool) -> None:
        """
        Test the `not_found_loggedout` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - If the user is not logged in, the status code is 404.
        - If the user is logged in, the status code is 200.
        """
        status_code = status.HTTP_200_OK if with_session else status.HTTP_404_NOT_FOUND

        response = self.get_request(f"{self.tenant_x_url}/contact", with_session)

        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.url, f"{self.tenant_x_url}/contact")

    @ddt.data(False, True)
    def test_redirect_loggedin(self, with_session: bool) -> None:
        """
        Test the `redirect_loggedin` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 200.
        - If the user is logged in, redirect to the configured URL.
        - If the user is not logged in, the URL is the requested URL.
        """
        final_path = "donate" if with_session else "courses"

        response = self.get_request(f"{self.tenant_x_url}/courses", with_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/{final_path}")
        if with_session:
            self.assertEqual(response.history[0].status_code, status.HTTP_302_FOUND)

    @ddt.data(False, True)
    def test_redirect_loggedout(self, with_session: bool) -> None:
        """
        Test the `redirect_loggedout` feature.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 200.
        - If the user is not logged in, redirect to the configured URL.
        - If the user is logged in, the URL is the requested URL.
        """
        final_path = "faq" if with_session else "donate"

        response = self.get_request(f"{self.tenant_x_url}/faq", with_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/{final_path}")
        if not with_session:
            self.assertEqual(response.history[0].status_code, status.HTTP_302_FOUND)

    @ddt.data(False, True)
    def test_mktg_redirect_with_empty_string(self, with_session: bool) -> None:
        """
        Test the `mktg_redirect` feature with an empty string.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The status code is 200.
        - The URL is the same as the requested URL.
        """
        response = self.get_request(f"{self.tenant_x_url}/about", with_session)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, f"{self.tenant_x_url}/about")

    @ddt.data(False, True)
    def test_mktg_redirect_with_other_url(self, with_session: bool) -> None:
        """
        Test the `mktg_redirect` feature with a different URL.

        Open edX definitions tested:
        - `configuration_helper.has_override_value`
        - `configuration_helper.get_value`

        Expected result:
        - The history contains a 302 status code.
        - The status code is 200.
        - The URL is the configured redirect URL.
        """
        response = self.get_request(f"{self.tenant_x_url}/dashboard", with_session)

        self.assertEqual(response.history[0].status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.url, "https://www.example.com/")
