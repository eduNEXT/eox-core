"""
Integration test suite.

This suite performs multiple http requests to guarantee
that the Grade API is behaving as expected on a live server.
"""
import json
from os import environ

import pytest
import requests
from django.test import TestCase
from rest_framework import status


@pytest.mark.skipif(not environ.get("TEST_INTEGRATION"), reason="Run only explicitly")
class TesteGradeIntegration(TestCase):  # pragma: no cover
    """Test suite"""

    data = {}

    @classmethod
    def setUpClass(cls):
        with open("eox_core/tests/integration/test_data") as file_obj:
            cls.data = json.load(file_obj)
        cls.data["endpoint"] = "eox-core/api/v1/grade/"
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
        cls.data["site1_data"]["token"] = response_site1.json()["access_token"]
        cls.data["site2_data"]["token"] = response_site2.json()["access_token"]

        create_enrollment(cls.data)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_read_valid_default_params(self):
        # pylint: disable=invalid-name
        """
        Get grades info from a user enrolled on a course without the optional
        fields.
        """
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

        response = requests.get(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("earned_grade", response_content)
        self.assertNotIn("grading_policy", response_content)
        self.assertNotIn("section_breakdown", response_content)

    def test_read_detail_no_policy(self):
        # pylint: disable=invalid-name
        """
        Get grades info from a user enrolled on a course. Include detailed info
        for each graded subsection.
        """
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "detailed": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("earned_grade", response_content)
        self.assertIn("section_breakdown", response_content)
        self.assertNotIn("grading_policy", response_content)

    def test_read_policy_detail(self):
        # pylint: disable=invalid-name
        """
        Get grades info from a user enrolled on a course. Include all extra info
        (subsection details and grading policy)
        """
        site1_data = self.data["site1_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "detailed": True,
            "grading_policy": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site1_data["token"]),
            "Host": site1_data["host"],
        }
        request_url = "{}/{}".format(site1_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)
        response_content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("earned_grade", response_content)
        self.assertIn("section_breakdown", response_content)
        self.assertIn("grading_policy", response_content)
        self.assertIn("grader", response_content["grading_policy"])
        self.assertIn("grade_cutoffs", response_content["grading_policy"])

    def test_read_invalid_enrollment_for_site(self):
        # pylint: disable=invalid-name
        """
        Get grade info for a user and course from another site.
        """
        site1_data = self.data["site1_data"]
        site2_data = self.data["site2_data"]
        data = {
            "email": site1_data["user_email"],
            "course_id": site1_data["course"]["id"],
            "detailed": True,
            "grading_policy": True,
        }
        headers = {
            "Authorization": "Bearer {}".format(site2_data["token"]),
            "Host": site2_data["host"],
        }
        request_url = "{}/{}".format(site2_data["base_url"], self.data["endpoint"])

        response = requests.get(request_url, data=data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
    request_url = "{}/{}".format(
        data["site1_data"]["base_url"], "eox-core/api/v1/enrollment/"
    )
    response = requests.post(request_url, data=req_data, headers=headers)
    response.raise_for_status()
