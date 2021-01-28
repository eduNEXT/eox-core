"""
Integration test suite.

This suite performs multiple http requests to guarantee
that all CRUD operations are handled correctly.
"""
import json
from os import environ

import pytest
import requests
from django.test import TestCase


@pytest.mark.skipif(not environ.get("TEST_INTEGRATION"), reason="Run only explicitly")
class TestEnrollmentIntegration(TestCase):  # pragma: no cover
    # pylint: disable=too-many-public-methods
    """Test suite"""
    data = {}

    @classmethod
    def setUpClass(cls):
        with open("eox_core/tests/integration/test_data") as file_obj:
            cls.data = json.load(file_obj)
        cls.data["endpoint"] = "eox-core/api/v1/enrollment/"
        site1_data = {
            "client_id": cls.data["site1_data"]["client_id"],
            "client_secret": cls.data["site1_data"]["client_secret"],
            "grant_type": "client_credentials",
        }
        site2_data = {
            "client_id": cls.data["site2_data"]["client_id"],
            "client_secret": cls.data["site2_data"]["client_secret"],
            "grant_type": "client_credentials",
        }
        request_url = "{}/{}".format(
            cls.data["site1_data"]["base_url"], "oauth2/access_token/"
        )
        response_site1 = requests.post(request_url, data=site1_data)
        response_site1.raise_for_status()
        cls.data["site1_data"]["token"] = response_site1.json()["access_token"]
        request_url = "{}/{}".format(
            cls.data["site2_data"]["base_url"], "oauth2/access_token/"
        )
        response_site2 = requests.post(request_url, data=site2_data)
        response_site2.raise_for_status()
        cls.data["site2_data"]["token"] = response_site2.json()["access_token"]

    @classmethod
    def tearDownClass(cls):
        delete_enrollment(cls.data)

    def test_read_valid_email_course(self):
        # pylint: disable=invalid-name
        """
        Get a valid enrollment
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        expected_response = {
            "username": site1_data["user_id"],
            "course_id": data["course_id"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(expected_response, response_content)

    def test_read_invalid_enrollment(self):
        # pylint: disable=invalid-name
        """
        Get a invalid enrollment (doesn't exist)
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "username": site1_data["user_id"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 404)

    def test_read_invalid_enrollment_for_site(self):
        # pylint: disable=invalid-name
        """
        Get a invalid enrollment (enrollment from other site)
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        site2_data = self.data["site2_data"]
        data = {
            "username": site1_data["user_id"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site2_data["token"]),
            "Host": site2_data["host"],
        }
        request_url = "{}/{}".format(site2_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 404)

    def test_create_enrollment_valid_user_mode_course(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid user, valid course,
        valid mode
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "mode": site1_data["course"]["mode"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_force_create_enrollment_valid_user_mode_course(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid user, valid course,
        valid mode using force
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "mode": site1_data["course"]["mode"],
            "force": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_create_valid_course_mode_invalid_user(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid course, valid mode,
        and a non-existent user
        """
        site1_data = self.data["site1_data"]
        data = {
            "username": site1_data["fake_user"],
            "course_id": site1_data["course"]["id"],
            "mode": site1_data["course"]["mode"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 400)

    def test_create_valid_course_mode_invalid_user_for_site(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid course, valid mode,
        and a user from another site
        """
        site1_data = self.data["site1_data"]
        site2_data = self.data["site2_data"]
        data = {
            "email": site2_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "mode": site1_data["course"]["mode"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 202)

    def test_create_valid_user_mode_invalid_course(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid user, valid mode,
        and non-existent course
        """
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": "fake_course_id",
            "mode": "audit",
            "force": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 400)

    def test_create_valid_user_mode_invalid_course_for_site(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid user, valid mode,
        and a course from another site
        """
        site1_data = self.data["site1_data"]
        site2_data = self.data["site2_data"]
        data = {
            "email": site2_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "mode": site1_data["course"]["mode"],
            "force": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site2_data["token"]),
            "Host": site2_data["host"],
        }
        request_url = "{}/{}".format(site2_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 400)

    # NOTE: Mode changes are not working correctly on devstack
    def test_force_create_valid_user_course_invalid_mode(self):
        # pylint: disable=invalid-name
        """
        Create enrollment with a valid user, valid course,
        and a not available mode
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "mode": "masters",
            "force": 1,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 400)

    def test_delete_valid_enrollment(self):
        # pylint: disable=invalid-name
        """
        Delete a valid enrollment
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.delete(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 204)

    def test_delete_invalid_enrollment(self):
        # pylint: disable=invalid-name
        """
        Delete a invalid enrollment(doesn't exist)
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.delete(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 404)

    def test_delete_invalid_enrollment_for_site(self):
        # pylint: disable=invalid-name
        """
        Delete a invalid enrollment (enrollment from other site)
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        site2_data = self.data["site2_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site2_data["token"]),
            "Host": site2_data["host"],
        }
        request_url = "{}/{}".format(site2_data["base_url"], self.data["endpoint"])

        response = requests.delete(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 404)

    def test_update_valid_enrollment_change_is_active(self):
        # pylint: disable=invalid-name
        """
        Update an existing enrollment; change is_active flag
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": False,
            "mode": site1_data["course"]["mode"],
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        expected_response = {
            "user": site1_data["user_id"],
            "is_active": False,
            "course_id": data["course_id"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(expected_response, response_content)

    # NOTE: Mode changes are not working correctly on devstack
    def test_update_valid_enrollment_change_valid_mode(self):
        # pylint: disable=invalid-name
        """
        Update an existing enrollment; change mode
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": True,
            "mode": "honor",
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        expected_response = {
            "user": site1_data["user_id"],
            "is_active": True,
            "course_id": data["course_id"],
            "mode": "honor",
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(expected_response, response_content)

    def test_update_valid_enrollment_change_invalid_mode(self):
        # pylint: disable=invalid-name
        """
        Update an existing enrollment; change to invalid mode
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": True,
            "mode": "masters",
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 400)

    def test_update_invalid_enrollment_change_valid_mode(self):
        # pylint: disable=invalid-name
        """
        Update an non-existent enrollment; change mode
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": True,
            "mode": "honor",
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 202)

    def test_update_invalid_enrollment_change_is_active(self):
        # pylint: disable=invalid-name
        """
        Update an non-existent enrollment; change is_active flag
        """
        delete_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": False,
            "mode": "audit",
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)

        self.assertEqual(response.status_code, 202)

    def test_update_valid_enrollment_change_is_active_force_post(self):
        # pylint: disable=invalid-name
        """
        Update an existing enrollment using POST with force=True;
        change is_active flag
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": False,
            "mode": site1_data["course"]["mode"],
            "force": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        expected_response = {
            "username": site1_data["user_id"],
            "is_active": False,
            "course_id": data["course_id"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.post(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(expected_response, response_content)

    # NOTE: Mode changes are not working correctly on devstack
    def test_update_valid_enrollment_change_valid_mode_force_post(self):
        # pylint: disable=invalid-name
        """
        Update an existing enrollment; change mode
        """
        create_enrollment(self.data)
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "is_active": True,
            "mode": "honor",
            "force": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        expected_response = {
            "user": site1_data["user_id"],
            "is_active": True,
            "course_id": data["course_id"],
            "mode": "honor",
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.put(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(expected_response, response_content)


def create_enrollment(data):
    """
    Auxiliary function to setUp test fixtures. Creates/enables a new enrollment.

    :param data: dictionary with all the parameters needed to create an enrollment.
    """
    req_data = {
        "email": data["site1_data"]["user_email"],
        "course_id": data["site1_data"]["course"]["id"],
        "mode": data["site1_data"]["course"]["mode"],
    }
    headers = {
        "Authorization": "Bearer {}".format(data["site1_data"]["token"]),
        "Host": data["site1_data"]["host"],
    }
    request_url = "{}/{}".format(data["site1_data"]["base_url"], data["endpoint"])
    response = requests.post(request_url, data=req_data, headers=headers)
    response.raise_for_status()


def delete_enrollment(data):
    """
    Auxiliary function to setUp test fixtures. Deletes an enrollment if exists.

    :param data: dictionary with all the parameters needed to delete an enrollment.
    """
    req_data = {
        "email": data["site1_data"]["user_email"],
        "course_id": data["site1_data"]["course"]["id"],
    }
    headers = {
        "Authorization": "Bearer {}".format(data["site1_data"]["token"]),
        "Host": data["site1_data"]["host"],
    }
    request_url = "{}/{}".format(data["site1_data"]["base_url"], data["endpoint"])
    response = requests.delete(request_url, data=req_data, headers=headers)
    if response.status_code == 404:
        return
    response.raise_for_status()
