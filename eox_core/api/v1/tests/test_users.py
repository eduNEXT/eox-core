"""
Test module for users viewset.
"""
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient

from eox_core.api.v1.serializers import EdxappUserQuerySerializer


class UsersUpdaterAPITest(TestCase):
    """Test class for EdxappUserUpdater viewset."""

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """Setup method for test class."""
        self.user = User(username="test", email="test@example.com", password="testtest")
        self.client = APIClient()
        self.url = reverse("eox-api:eox-api:edxapp-user-updater")
        self.client.force_authenticate(user=self.user)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch('eox_core.api.v1.views.EdxappUserReadOnlySerializer')
    def test_update_success(self, user_serializer, get_edxapp_user, signup_source, _):
        """Used to test updating safe fields of an edxapp user."""
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        user_serializer.return_value.data = {}
        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_update_bad_sign_up_source(self, get_edxapp_user, signup_source, _):
        """Used to test that when an user has more than one signup source then the update can't be done."""
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        get_edxapp_user.return_value = self.user
        signup_source.objects.filter.return_value.count.return_value = 2

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with more than one sign up source."]}'
                         .encode())

    @patch_permissions
    @patch('eox_core.api.v1.serializers.UserSignupSource')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_update_role_not_allowed(self, get_edxapp_user, signup_source, _):
        """Used to test that if an user is staff or superuser then the update can't be done.ss"""
        user = User(username="test", email="test@example.com", password="testtest", is_staff=True)
        update_data = {
            "email": "test",
            "fullname": "test",
        }
        get_edxapp_user.return_value = user
        signup_source.objects.filter.return_value.count.return_value = 1

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"detail":["You can\'t update users with roles like staff or superuser."]}'
                         .encode())


@override_settings(
    extended_profile_fields=[
        "father_last_name",
        "mother_last_name",
        "type_document",
        "personal_id",
        "mobile",
        "address",
    ],
    EDNX_CUSTOM_REGISTRATION_FIELDS=[
        {
            "label": "Father last name",
            "name": "father_last_name",
            "type": "text",
        },
        {
            "label": "Mother last name",
            "name": "mother_last_name",
            "type": "text",
        },
        {
            "label": "Document type",
            "name": "type_document",
            "options": [
                "dni",
                "passport",
                "license",
            ],
            "type": "select",
            "default": "dni",
        },
        {
            "label": "Document number",
            "name": "personal_id",
            "type": "text",
        },
        {
            "label": "Mobile",
            "name": "mobile",
            "type": "text",
            "restrictions": {
                "max_length": 12,
            }
        },
        {
            "label": "Address",
            "name": "address",
            "type": "text",
        },
    ],
    REGISTRATION_EXTRA_FIELDS={
        "address": "required",
        "country": "required",
        "father_last_name": "required",
        "goals": "required",
        "mailing_address": "hidden",
        "mobile": "required",
        "mother_last_name": "required",
        "personal_id": "required",
        "type_document": "required",
        "year_of_birth": "hidden",
    },
)
class UsersAPITest(TestCase):
    """Test class for users viewset."""

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """Setup method for test class."""
        self.gender_choices = (
            ('m', 'Male'),
            ('f', 'Female'),
            ('o', 'Other/Prefer Not to Say')
        )
        self.level_of_education_choices = (
            ('p', 'Doctorate'),
            ('m', 'Master or professional degree'),
            ('el', 'Elementary/primary school'),
            ('none', 'No formal education'),
            ('other', 'Other education')
        )
        self.user = User(username="test", email="test@example.com", password="testtest")
        self.client = APIClient()
        self.url = reverse("eox-api:eox-api:edxapp-user")
        self.client.force_authenticate(user=self.user)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.check_edxapp_account_conflicts')
    @patch('eox_core.api.v1.serializers.get_gender_choices')
    @patch('eox_core.api.v1.serializers.get_level_of_education_choices')
    def test_success(self, mock_level_education_choices, mock_gender_choices, mock_check_account_conflicts, _):
        """test when the request data is correct and complete
        the serializer is valid.
        """
        request_data = {
            "username": "AleMagno",
            "email": "alexTheGreat@example.com",
            "password": "p@ssword",
            "fullname": "Alexander",
            "mother_last_name": "Perez",
            "type_document": "dni",
            "father_last_name": "Magno",
            "personal_id": "0900172",
            "mobile": "04143472044",
            "address": "Pella",
            "country": "gr",
            "goals": "to have all the people in the places I have conquered accept me as their ruler.",
        }
        mock_level_education_choices.return_value = self.level_of_education_choices
        mock_gender_choices.return_value = self.gender_choices
        mock_check_account_conflicts.return_value = False

        serializer = EdxappUserQuerySerializer(data=request_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set([]))

    @patch_permissions
    @patch('eox_core.api.v1.serializers.check_edxapp_account_conflicts')
    @patch('eox_core.api.v1.serializers.get_gender_choices')
    @patch('eox_core.api.v1.serializers.get_level_of_education_choices')
    @patch('eox_core.api.v1.views.create_edxapp_user')
    def test_missing_required_fields(self, create_edxapp_user, mock_level_education_choices, mock_gender_choices, mock_check_account_conflicts, _):
        """tests case when the request data has missing required fields,
        the registration process is not successful.
        """
        request_data = {
            "username": "AleMagno",
            "email": "alexTheGreat@example.com",
            "password": "p@ssword",
            "fullname": "Alexander",
            "mother_last_name": "Perez",
            "type_document": "dni",
            "father_last_name": "Magno",
            "personal_id": "0900172",
            "mobile": "04143472044",
            "address": "Pella",
            "goals": "to have all the people in the places I have conquered accept me as their ruler.",
        }
        mock_level_education_choices.return_value = self.level_of_education_choices
        mock_gender_choices.return_value = self.gender_choices
        mock_check_account_conflicts.return_value = False

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"country":["This field is required."]}'
                         .encode())

    @patch_permissions
    @patch('eox_core.api.v1.serializers.check_edxapp_account_conflicts')
    @patch('eox_core.api.v1.serializers.get_gender_choices')
    @patch('eox_core.api.v1.serializers.get_level_of_education_choices')
    @patch('eox_core.api.v1.views.create_edxapp_user')
    def test_wrong_option_in_select_field(self, create_edxapp_user, mock_level_education_choices, mock_gender_choices, mock_check_account_conflicts, _):
        """tests case when the request data has an invalid option in a custom select field,
        the registration process is not successful.
        """
        request_data = {
            "username": "AleMagno",
            "email": "alexTheGreat@example.com",
            "password": "p@ssword",
            "fullname": "Alexander",
            "mother_last_name": "Perez",
            "type_document": "credit card",
            "father_last_name": "Magno",
            "personal_id": "0900172",
            "mobile": "04143472044",
            "address": "Pella",
            "country": "gr",
            "goals": "to have all the people in the places I have conquered accept me as their ruler.",
        }
        mock_level_education_choices.return_value = self.level_of_education_choices
        mock_gender_choices.return_value = self.gender_choices
        mock_check_account_conflicts.return_value = False

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"type_document":["\\"credit card\\" is not a valid choice."]}'
                         .encode())

    @patch_permissions
    @patch('eox_core.api.v1.serializers.check_edxapp_account_conflicts')
    @patch('eox_core.api.v1.serializers.get_gender_choices')
    @patch('eox_core.api.v1.serializers.get_level_of_education_choices')
    def test_default_in_select_field(self, mock_level_education_choices, mock_gender_choices, mock_check_account_conflicts, _):
        """tests the case when a custom field of type select is required
        and has a default value, the serializer is valid.
        """
        request_data = {
            "username": "AleMagno",
            "email": "alexTheGreat@example.com",
            "password": "p@ssword",
            "fullname": "Alexander",
            "mother_last_name": "Perez",
            "father_last_name": "Magno",
            "personal_id": "0900172",
            "mobile": "04143472044",
            "address": "Pella",
            "country": "gr",
            "goals": "to have all the people in the places I have conquered accept me as their ruler.",
        }
        mock_level_education_choices.return_value = self.level_of_education_choices
        mock_gender_choices.return_value = self.gender_choices
        mock_check_account_conflicts.return_value = False

        serializer = EdxappUserQuerySerializer(data=request_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set([]))

    @patch_permissions
    @patch('eox_core.api.v1.serializers.check_edxapp_account_conflicts')
    @patch('eox_core.api.v1.serializers.get_gender_choices')
    @patch('eox_core.api.v1.serializers.get_level_of_education_choices')
    @patch('eox_core.api.v1.views.create_edxapp_user')
    def test_restriction_in_text_field(self, create_edxapp_user, mock_level_education_choices, mock_gender_choices, mock_check_account_conflicts, _):
        """tests that the validations of a custom field of type 'text'
        are being made. In this case the mobile field exceeds the max_length
        defined in the settings.
        """
        request_data = {
            "username": "AleMagno",
            "email": "alexTheGreat@example.com",
            "password": "p@ssword",
            "fullname": "Alexander",
            "mother_last_name": "Perez",
            "type_document": "dni",
            "gender": "m",
            "father_last_name": "Magno",
            "personal_id": "0900172",
            "mobile": "0414347204400999",
            "address": "Pella",
            "country": "gr",
            "goals": "graduate",
        }
        mock_level_education_choices.return_value = self.level_of_education_choices
        mock_gender_choices.return_value = self.gender_choices
        mock_check_account_conflicts.return_value = False

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.content, '{"mobile":["Ensure this field has no more than 12 characters."]}'
                         .encode())
