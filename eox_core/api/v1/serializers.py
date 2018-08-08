"""
API v1 serializers.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers

from eox_core.edxapp_wrapper.users import check_edxapp_account_conflicts


class EdxappUserSerializer(serializers.Serializer):
    """
    Handles the serialization of the user data required to create an edxapp user
    on different backends
    """

    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)  # Can be updated to 150 after django 1.11 has settled in
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
    )
    fullname = serializers.CharField(max_length=255, write_only=True)  # write_only so the user object does not complain for having the name at get_full_name()

    # Extra info to be returned by the api after creating the user
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    def validate(self, data):
        """
        Check that there are no conflicts on the accounts
        """
        email = data.get("email")
        username = data.get("username")
        conflicts = check_edxapp_account_conflicts(email, username)
        if conflicts:
            raise serializers.ValidationError("Account already exists with the provided: {}".format(", ".join(conflicts)))
        return data


class EdxappUserQuerySerializer(EdxappUserSerializer):
    """
    Handles the serialization of the context data required to create an edxapp user
    on different backends
    """

    activate_user = serializers.BooleanField(default=False)  # We need to allow the api to activate users later on


class EdxappCourseEnrollmentSerializer(serializers.Serializer):
    """Serializes CourseEnrollment

    Aggregates all data from the Course Enrollment table, and pulls in the serialization for
    the Course Descriptor and course modes, to give a complete representation of course enrollment.

    """
    HONOR = 'honor'
    PROFESSIONAL = 'professional'
    VERIFIED = 'verified'
    AUDIT = 'audit'
    NO_ID_PROFESSIONAL_MODE = 'no-id-professional'
    CREDIT_MODE = 'credit'
    ALL_MODES = [AUDIT, CREDIT_MODE, HONOR, NO_ID_PROFESSIONAL_MODE, PROFESSIONAL, VERIFIED, ]

    user = serializers.CharField(max_length=30)
    created = serializers.DateTimeField(allow_null=True)
    is_active = serializers.BooleanField(default=True)
    mode = serializers.CharField(default=AUDIT, max_length=100)

    def validate(self, data):
        return data


class EdxappCourseEnrollmentQuerySerializer(EdxappCourseEnrollmentSerializer):
    """
    Handles the serialization of the context data required to create an enrollemnt
    on different backends
    """
    force_registration = serializers.BooleanField(default=False)
