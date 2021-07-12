"""
API v1 serializers.
"""
# pylint: disable=abstract-method
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from django.conf import settings
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework.fields import HiddenField

from eox_core.edxapp_wrapper.coursekey import get_valid_course_key, validate_org
from eox_core.edxapp_wrapper.enrollments import check_edxapp_enrollment_is_valid
from eox_core.edxapp_wrapper.users import (
    check_edxapp_account_conflicts,
    get_user_read_only_serializer,
    get_user_signup_source,
    get_username_max_length,
)
from eox_core.utils import (
    create_user_profile,
    get_gender_choices,
    get_level_of_education_choices,
    get_registration_extra_fields,
    get_valid_years,
    set_custom_field_restrictions,
    set_select_custom_field,
)

UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name

MAX_SIGNUP_SOURCES_ALLOWED = 1

USERNAME_MAX_LENGTH = get_username_max_length()

ALLOWED_TYPES = ["text", "email", "select", "textarea", "checkbox", "plaintext", "password", "hidden"]

YEAR_OF_BIRTH_CHOICES = [(str(year), str(year)) for year in get_valid_years()]


class EdxappWithWarningSerializer(serializers.Serializer):
    """
    Mixin serializer to add a warning field to Edxapp serializers
    """
    def __init__(self, *args, **kwargs):
        """
        Conditionally adds a warning field if a context is passed
        """
        super(EdxappWithWarningSerializer, self).__init__(*args, **kwargs)

        # This field should only exist if a context is actually passed to the serializer
        if self.context:
            self.fields['warning'] = serializers.SerializerMethodField(read_only=True)

    warning = serializers.CharField(read_only=True, required=False)

    def get_warning(self, obj):
        """Set the warning from the context"""
        if self.context:
            return self.context
        return None


class EdxappUserSerializer(serializers.Serializer):
    """
    Handles the serialization of the user data required to create an edxapp user
    on different backends
    """

    email = serializers.EmailField()
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
    )
    fullname = serializers.CharField(max_length=255, write_only=True)  # write_only so the user object does not complain for having the name at get_full_name()

    # Extra info to be returned by the api after creating the user
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        """
        Check that there are no conflicts on the accounts
        """
        email = attrs.get("email")
        username = attrs.get("username")
        conflicts = check_edxapp_account_conflicts(email, username)
        if conflicts:
            raise serializers.ValidationError("Account already exists with the provided: {}".format(", ".join(conflicts)))
        return attrs


class EdxappExtendedUserSerializer(EdxappUserSerializer):
    """
    This serializer allows admiting all the
    UserProfile fields and also the extra fields for the
    userProfile.meta values that are specified in the
    microsite settings.

    If "terms_of_service" or "honor_code" are not marked
    as hidden fields in the REGISTRATION_EXTRA_FIELDS setting,
    then they are added as hidden fields in the serializer
    with the default value set to "true", so these terms
    and conditions are "accepted" when using the create-user
    endpoint.
    """
    year_of_birth = serializers.ChoiceField(choices=YEAR_OF_BIRTH_CHOICES)
    gender = serializers.ChoiceField(choices=get_gender_choices())
    city = serializers.CharField()
    goals = serializers.CharField()
    bio = serializers.CharField(max_length=3000)
    profile_image_uploaded_at = serializers.DateTimeField()
    phone_number = serializers.CharField(max_length=50)
    mailing_address = serializers.CharField()
    courseware = serializers.CharField(max_length=255)
    level_of_education = serializers.ChoiceField(choices=get_level_of_education_choices())
    country = CountryField(required=False)
    terms_of_service = serializers.HiddenField(default='true')
    honor_code = serializers.HiddenField(default='true')

    def __init__(self, *args, **kwargs):  # pylint: disable=too-many-locals
        """
        Add the custom registration fields specified in the settings.
        """
        super().__init__(*args, **kwargs)

        extended_profile_fields = getattr(settings, "extended_profile_fields", [])
        extra_fields = get_registration_extra_fields()
        ednx_custom_registration_fields = getattr(settings, "EDNX_CUSTOM_REGISTRATION_FIELDS", [])
        all_fields = set(self.fields)
        # Obtain only the fields defined in the EdxappExtendedUserSerializer
        non_profile_fields = set(EdxappUserSerializer().fields)
        non_profile_fields.update(["activate_user", "skip_password"])
        profile_fields = all_fields - non_profile_fields

        # Delete the profile fields that are not allowed or are redefined in the ednx_custom_registration setting
        # In case the field IS allowed, check if is required or not
        for field in profile_fields:
            if field not in extra_fields or field in extended_profile_fields:
                self.fields.pop(field)
            else:
                # Hidden fields take their value from the default, so we should not alter the "required" attribute.
                if not isinstance(self.fields[field], HiddenField):
                    self.fields[field].required = extra_fields.get(field) == "required"

        # Adding fields that go inside the UserProfile.meta
        for custom_field in ednx_custom_registration_fields:
            field_name = custom_field.get("name")
            field_type = custom_field.get("type")

            if field_name in extended_profile_fields and field_type in ALLOWED_TYPES:
                serializer_field = {}

                serializer_field["required"] = extra_fields.get(field_name) == "required"

                # Check this first since fields of type 'text' are the only ones that can have restrictions
                if field_type == "text":
                    serializer_field = set_custom_field_restrictions(custom_field, serializer_field)

                # Now we add the field to the serializer according to the custom field type defined in the settings
                if field_type == "select":
                    self.fields[field_name] = serializers.ChoiceField(**set_select_custom_field(custom_field, serializer_field))

                elif field_type == "checkbox":
                    self.fields[field_name] = serializers.BooleanField(**serializer_field)

                else:
                    self.fields[field_name] = serializers.CharField(**serializer_field)


class WrittableEdxappUserSerializer(EdxappExtendedUserSerializer):
    """
    Handles the serialization of the user data required to update an edxapp user.
    """
    password = serializers.CharField(
        style={'input_type': 'password'},
    )
    is_active = serializers.BooleanField()

    def validate(self, attrs):
        """
        When an update is being made, then it checks that the user:
            - Is not staff or superuser.
            - Has just one signup source.
            - The field being updated is a safe field.
        """
        # If at least one of these conditions is true, then the user can't be updated.
        safe_fields = getattr(settings, "EOX_CORE_USER_UPDATE_SAFE_FIELDS", [])

        for attr in attrs:
            if attr not in safe_fields:
                raise serializers.ValidationError({"detail": "You are not allowed to update {}.".format(attr)})

        if self.instance.is_staff or self.instance.is_superuser:
            raise serializers.ValidationError({"detail": "You can't update users with roles like staff or superuser."})

        if UserSignupSource.objects.filter(user__email=self.instance.email).count() > MAX_SIGNUP_SOURCES_ALLOWED:
            raise serializers.ValidationError({"detail": "You can't update users with more than one sign up source."})

        return attrs

    def update(self, instance, validated_data):
        """
        Update method for safe fields.
        """
        extended_profile_fields = getattr(settings, 'extended_profile_fields', [])
        # Obtain only the User profile fields defined in the EdxappExtendedUserSerializer
        all_fields = set(EdxappExtendedUserSerializer().fields)
        non_profile_fields = set(EdxappUserSerializer().fields)
        extra_registration_fields = all_fields - non_profile_fields
        # Check if the User has a Profile
        has_profile = hasattr(instance, 'profile')

        extra_registration_fields.update(extended_profile_fields)
        if has_profile:
            profile_meta = instance.profile.get_meta()

        for key, value in validated_data.items():

            if key == "password":
                instance.set_password(value)

            elif key in extra_registration_fields or key == "fullname":
                if not has_profile:
                    create_user_profile(instance)
                    profile_meta = {}
                    has_profile = True

                # First check if the field belongs to the meta
                if key in extended_profile_fields:
                    profile_meta[key] = value

                # Key is one of the user profile fields
                else:
                    if key == "year_of_birth":
                        value = int(value)
                    # 'name' field is sent as 'fullname' in the request
                    if key == "fullname":
                        key = "name"
                    setattr(instance.profile, key, value)

            else:
                setattr(instance, key, value)

        if validated_data:
            if has_profile:
                # Update user profile meta
                instance.profile.set_meta(profile_meta)
                instance.profile.save()
            instance.save()

        return instance


class EdxappUserQuerySerializer(EdxappExtendedUserSerializer):
    """
    Handles the serialization of the context data required to create an edxapp user
    on different backends
    """

    activate_user = serializers.BooleanField(default=False)  # We need to allow the api to activate users later on
    skip_password = serializers.BooleanField(default=False, write_only=True)

    def __init__(self, *args, **kwargs):  # pylint: disable=too-many-locals
        """
        Check skip_password flag to see if password
        should be omitted.
        """
        super().__init__(*args, **kwargs)

        initial_data = getattr(self, "initial_data", {})

        if initial_data.get("skip_password", False):  # pylint: disable=no-member
            self.fields.pop("password", None)


class EdxappEnrollmentAttributeSerializer(serializers.Serializer):
    """
    Attributes serializer
    """
    namespace = serializers.CharField()
    name = serializers.CharField()
    value = serializers.CharField()


class EdxappValidatedCourseIDField(serializers.Field):
    """
    CourseKey Field
    """
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        """
        Check course_id has the correct format and that it is allowed inside the org
        """
        if validate_org(data):  # pylint: disable=no-else-return
            return str(get_valid_course_key(data))
        else:
            raise serializers.ValidationError('Invalid course_id {}'.format(data))


class EdxappCourseEnrollmentSerializer(serializers.Serializer):
    """Serializes CourseEnrollment

    Aggregates all data from the Course Enrollment table, and pulls in the serialization for
    the Course Descriptor and course modes, to give a complete representation of course enrollment.

    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH, default=None, source='user')
    is_active = serializers.BooleanField(default=True)
    mode = serializers.CharField(max_length=100)
    enrollment_attributes = EdxappEnrollmentAttributeSerializer(many=True, required=False)
    course_id = EdxappValidatedCourseIDField()

    class Meta:
        """
        Add extra details for swagger
        """
        swagger_schema_fields = {
            "example": OrderedDict(
                [
                    ("username", "johndoe"),
                    ("is_active", True),
                    ("mode", "audit"),
                    ("enrollment_attributes", []),
                    ("course_id", "course-v1:edX+DemoX+Demo_Course")
                ]
            ),
        }

    def validate(self, attrs):
        """
        Check that there are no issues with enrollment
        """
        errors = check_edxapp_enrollment_is_valid(**attrs)
        if errors:
            raise serializers.ValidationError(", ".join(errors))
        return attrs


class EdxappCourseEnrollmentQuerySerializer(EdxappCourseEnrollmentSerializer):
    """
    Handles the serialization of the context data required to create an enrollment
    on different backends
    """
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH, default=None)
    email = serializers.CharField(max_length=255, default=None)
    force = serializers.BooleanField(default=False)
    course_id = EdxappValidatedCourseIDField(default=None)
    bundle_id = serializers.CharField(max_length=255, default=None)


class EdxappCoursePreEnrollmentSerializer(EdxappWithWarningSerializer):
    """Serialize CourseEnrollmentAllowed

    Handles the serialization of the context data required to create a course whitelisting or pre-enrollments for a user
    """
    course_id = EdxappValidatedCourseIDField()
    auto_enroll = serializers.BooleanField(default=True)
    email = serializers.EmailField()


def EdxappUserReadOnlySerializer(*args, **kwargs):   # pylint: disable=invalid-name
    """
    Fake class to lazily retrieve UserReadOnlySerializer
    """
    return get_user_read_only_serializer()(*args, **kwargs)


class EdxappSectionBreakdownSerializer(serializers.Serializer):
    """
    Serializes the `section_breakdown` portion of the Grades API.
    """
    attempted = serializers.BooleanField()
    assignment_type = serializers.CharField()
    percent = serializers.FloatField()
    score_earned = serializers.FloatField()
    score_possible = serializers.FloatField()
    subsection_name = serializers.CharField()


class EdxappGradingRawPolicySerializer(serializers.Serializer):
    """
    Serializes the items in the GRADER part of grading policy.
    """
    assignment_type = serializers.CharField(source='type')
    count = serializers.IntegerField(source='min_count')
    dropped = serializers.IntegerField(source='drop_count')
    weight = serializers.FloatField()


class EdxappGradingPolicySerializer(serializers.Serializer):
    """
    Serializes the course grading policy
    """
    grader = EdxappGradingRawPolicySerializer(many=True, source="GRADER")
    grade_cutoffs = serializers.DictField(child=serializers.FloatField(), source="GRADE_CUTOFFS")


class EdxappGradeSerializer(serializers.Serializer):
    """
    Serializes the grades data for a user in a given course
    """
    earned_grade = serializers.FloatField()
    grading_policy = EdxappGradingPolicySerializer(required=False)
    section_breakdown = EdxappSectionBreakdownSerializer(many=True, required=False)

    class Meta:
        """
        Add extra details for swagger
        """
        swagger_schema_fields = {
            "example":
            {
                "earned_grade": 0.5,
                "grading_policy": {
                    "grader": [
                        {
                            "assignment_type": "Homework",
                            "count": 1,
                            "dropped": 0,
                            "weight": 1.0
                        }
                    ],
                    "grade_cutoffs": {
                        "Pass": 0.5
                    }
                },
                "section_breakdown": [
                    {
                        "attempted": True,
                        "assignment_type": "Homework",
                        "percent": 0.5,
                        "score_earned": 5,
                        "score_possible": 10,
                        "subsection_name": "Homework - Questions"
                    }
                ]
            }
        }
