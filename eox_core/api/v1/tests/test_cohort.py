"""
Test module for the User Cohort API.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from mock import MagicMock, patch
from rest_framework import status
from rest_framework.test import APITestCase


class TestUserCohortAPI(APITestCase):
    """Tests class fort UserCohort API endpoints."""

    def setUp(self):
        """Setup method for test class."""
        self.api_user = User(1, "api_user@example.com", "api_user")
        self.test_user = User(2, "test@example.com", "test")
        self.client.force_authenticate(user=self.api_user)  # pylint: disable=no-member
        self.url = reverse("eox-api:eox-api:edxapp-cohort")
        self.test_user_cohort = MagicMock()
        self.test_user_cohort.name = "Team 1"
        self.api_user_cohort = MagicMock()
        self.api_user_cohort.name = "Team 2"

    @patch("eox_core.api.v1.views.get_user_cohort")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    def test_get_cohort_name(self, get_user_mock, _, get_cohort_mock):
        """
        Used to test that the users cohort name can be retrieved given a course and a username.
        """
        query_params = {
            "username": "test",
            "course_id": "course-v1:edX+DemoX+Demo_Course",
        }
        get_user_mock.return_value = self.api_user
        get_cohort_mock.return_value = self.test_user_cohort
        expected_response = {
            "cohort_name": self.test_user_cohort.name,
        }

        response = self.client.get(self.url, query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("eox_core.api.v1.views.get_user_cohort")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    def test_user_without_cohort(self, get_user_mock, _, get_cohort_mock):
        """
        Used to test getting the name of a cohort with a user without cohort.
        """
        query_params = {
            "username": "test",
            "course_id": "course-v1:edX+DemoX+Demo_Course",
        }
        get_user_mock.return_value = self.api_user
        get_cohort_mock.return_value = None

        response = self.client.get(self.url, query_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("eox_core.api.v1.views.get_user_cohort")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    def test_get_cohort_without_username(self, get_user_mock, _, get_cohort_mock):
        """
        Used to test getting the name of a cohort without username param.
        """
        query_params = {
            "course_id": "course-v1:edX+DemoX+Demo_Course",
        }
        get_cohort_mock.return_value = self.api_user_cohort
        expected_response = {
            "cohort_name": self.api_user_cohort.name,
        }

        response = self.client.get(self.url, query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("eox_core.api.v1.views.get_user_cohort")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    def test_get_cohort_without_course_id(self, get_user_mock, _, get_cohort_mock):
        """
        Used to test getting the name of a cohort without course_id param.
        """
        query_params = {
            "username": "test",
        }
        get_user_mock.return_value = self.api_user

        response = self.client.get(self.url, query_params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
