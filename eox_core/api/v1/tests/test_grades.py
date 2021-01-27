"""
Test module for the Grades API
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from mock import MagicMock, patch
from rest_framework import status
from rest_framework.test import APIClient

from eox_core.api.v1.views import EdxappGrade


class TestGradesAPI(TestCase):
    """ Tests for the grades endpoints """

    patch_permissions = patch(
        "eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission",
        return_value=True,
    )

    def setUp(self):
        """ setup """
        self.api_user = User(1, "test@example.com", "test")
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)
        self.url = reverse("eox-api:eox-api:edxapp-grade")

    @patch("eox_core.api.v1.views.get_courseware_courses")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_course_grade_factory")
    @patch("eox_core.api.v1.views.get_enrollment")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    @patch_permissions
    def test_get_grade_no_detail_no_policy(  # pylint: disable=too-many-arguments
            self,
            _,
            get_edxapp_user,
            get_enrollment,
            grade_factory,
            get_valid_course_key,
            get_courseware_courses,
    ):
        """Test that the GET method works with default parameters"""

        get_edxapp_user.return_value.username = "test"
        get_enrollment.return_value = None, None
        grade_factory.return_value.return_value.read.return_value.percent = 0.5
        params = {
            "course_id": "course-v1:org+course+run",
            "username": "test",
        }
        expected_response = {"earned_grade": 0.5}

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("eox_core.api.v1.views.get_courseware_courses")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_course_grade_factory")
    @patch("eox_core.api.v1.views.get_enrollment")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    @patch_permissions
    def test_get_grade_detail_no_policy(  # pylint: disable=too-many-arguments
            self,
            _,
            get_edxapp_user,
            get_enrollment,
            grade_factory,
            get_valid_course_key,
            get_courseware_courses,
    ):
        """Test that the GET method works including section details"""

        get_edxapp_user.return_value.username = "test"
        get_enrollment.return_value = None, None
        grade_factory.return_value.return_value.read.return_value.percent = 0.5
        grade_factory.return_value.return_value.read.return_value.subsection_grades = {}
        params = {
            "course_id": "course-v1:org+course+run",
            "username": "test",
            "detailed": True,
        }
        expected_response = {"earned_grade": 0.5, "section_breakdown": []}

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("eox_core.api.v1.views.get_courseware_courses")
    @patch("eox_core.api.v1.views.get_valid_course_key")
    @patch("eox_core.api.v1.views.get_course_grade_factory")
    @patch("eox_core.api.v1.views.get_enrollment")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    @patch_permissions
    def test_get_grade_detail_policy(  # pylint: disable=too-many-arguments
            self,
            _,
            get_edxapp_user,
            get_enrollment,
            grade_factory,
            get_valid_course_key,
            get_courseware_courses,
    ):
        """Test that the GET method works with section details and grading policy"""

        get_edxapp_user.return_value.username = "test"
        get_enrollment.return_value = None, None
        grade_factory.return_value.return_value.read.return_value.percent = 0.5
        grade_factory.return_value.return_value.read.return_value.subsection_grades = {}
        get_courseware_courses.return_value.get_course_by_id.return_value.grading_policy = {
            "GRADE_CUTOFFS": {},
            "GRADER": [],
        }
        params = {
            "username": "test",
            "course_id": "course-v1:org+course+run",
            "grading_policy": True,
            "detailed": True,
        }
        expected_response = {
            "earned_grade": 0.5,
            "grading_policy": {"grade_cutoffs": {}, "grader": []},
            "section_breakdown": [],
        }

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("eox_core.api.v1.views.get_enrollment")
    @patch("eox_core.api.v1.views.get_edxapp_user")
    @patch_permissions
    def test_get_grade_input_validation(self, _, get_edxapp_user, get_enrollment):
        """Test that the GET method fails if not all required parameters are provided"""
        params1 = {"username": "test"}
        params2 = {"course_id": "test:Course"}

        response1 = self.client.get(self.url)
        response2 = self.client.get(self.url, params1)
        response3 = self.client.get(self.url, params2)

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_section_breakdown(self):
        # pylint: disable=protected-access
        """Test the `_section_breakdown` helper function"""
        subsection_grade1 = MagicMock()
        subsection_grade2 = MagicMock()

        subsection_grade1.graded = True
        subsection_grade1.attempted_graded = True
        subsection_grade1.graded_total.earned = 10
        subsection_grade1.graded_total.possible = 10
        subsection_grade1.percent_graded = 1
        subsection_grade1.format = "Homework"
        subsection_grade1.display_name = "Homework - Questions"

        subsection_grade2.graded = False

        subsection_grades = {1: subsection_grade1, 2: subsection_grade2}
        section_breakdown = EdxappGrade()._section_breakdown(subsection_grades)

        expected_subgrades = [
            {
                "attempted": True,
                "assignment_type": "Homework",
                "percent": 1,
                "score_earned": 10,
                "score_possible": 10,
                "subsection_name": "Homework - Questions",
            }
        ]

        self.assertEqual(section_breakdown, expected_subgrades)
