"""Utilities for the integration test suite."""

from __future__ import annotations

import requests
from django.conf import settings as ds
from django.test import TestCase

settings = ds.INTEGRATION_TEST_SETTINGS


def get_access_token() -> str:
    """
    Get an access token for all requests in the test suite.

    Returns:
        str: The access token.
    """
    data = {
        "client_id": settings["CLIENT_ID"],
        "client_secret": settings["CLIENT_SECRET"],
        "grant_type": "client_credentials",
    }
    url = f"http://{settings['LMS_BASE']}/oauth2/access_token/"
    response = requests.post(url, data=data, timeout=settings["API_TIMEOUT"])
    return response.json()["access_token"]


ACCESS_TOKEN = get_access_token()


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
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    full_url = f"{tenant['base_url']}/{url}"

    method = method.upper()
    if method not in ("GET", "POST", "PATCH", "PUT", "DELETE"):
        raise ValueError(f"Unsupported HTTP method: {method}.")

    request = requests.request(
        method,
        full_url,
        json=json,
        data=data,
        params=params,
        headers=headers,
        timeout=settings["API_TIMEOUT"],
    )

    print('REQUEST TEST FELIPE' ,request)

    return request


class BaseIntegrationTest(TestCase):
    """
    Base class for the integration test suite.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class attributes.
        """
        super().__init__(*args, **kwargs)
        self.default_site = self.get_tenant_data()
        self.tenant_x = self.get_tenant_data("tenant-x")
        self.tenant_y = self.get_tenant_data("tenant-y")
        self.demo_course_id = settings["DEMO_COURSE_ID"]

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
