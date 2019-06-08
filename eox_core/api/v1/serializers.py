"""
API v1 serializers.
"""
# pylint: disable=abstract-method
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from eox_core.edxapp_wrapper.users import check_edxapp_account_conflicts, get_user_read_only_serializer
from eox_core.edxapp_wrapper.enrollments import check_edxapp_enrollment_is_valid
from eox_core.edxapp_wrapper.coursekey import validate_org, get_valid_course_key
from eox_core.edxapp_wrapper.pre_enrollments import validate_pre_enrollment



class EdxappWithWarningSerializer(serializers.Serializer):
    """
    Mixin serializer to add a warning field to Edxapp serializers
    """
    warning = serializers.SerializerMethodField('set_warning')

    def set_warning(self, obj):
        """Set the warning from the context"""
        if self.context:
            return self.context
        return ''


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


class EdxappUserQuerySerializer(EdxappUserSerializer):
    """
    Handles the serialization of the context data required to create an edxapp user
    on different backends
    """

    activate_user = serializers.BooleanField(default=False)  # We need to allow the api to activate users later on


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
        if validate_org(data):
            return str(get_valid_course_key(data))
        else:
            raise serializers.ValidationError('Course_id not allowed for given organization')


class EdxappCourseEnrollmentSerializer(serializers.Serializer):
    """Serializes CourseEnrollment

    Aggregates all data from the Course Enrollment table, and pulls in the serialization for
    the Course Descriptor and course modes, to give a complete representation of course enrollment.

    """

    username = serializers.CharField(max_length=30, default=None, source='user')
    is_active = serializers.BooleanField(default=True)
    mode = serializers.CharField(max_length=100)
    enrollment_attributes = EdxappEnrollmentAttributeSerializer(many=True, default=[])
    course_id = EdxappValidatedCourseIDField()

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
    username = serializers.CharField(max_length=30, default=None)
    email = serializers.CharField(max_length=255, default=None)
    force = serializers.BooleanField(default=False)
    course_id = EdxappValidatedCourseIDField(default=None)
    bundle_id = serializers.CharField(max_length=255, default=None)


class EdxappCoursePreEnrollmentSerializer(EdxappWithWarningSerializer):
    """Serialize CourseEnrollmentAllowed

    Handles the serialization of the context data required to create a course whitelisting or pre-enrollments for a user
    """
    course_id = serializers.CharField(max_length=255, default=None)
    auto_enroll = serializers.BooleanField(default=True)
    email = serializers.EmailField()

    def validate(self, attrs):
        """
        Check that there are no issues with the pre-enrollment
        """
        course_id = attrs.get("course_id", None)
        program_uuid = attrs.get('bundle_id', None)
        error = None

        if program_uuid and course_id:
            error = 'You have to provide a course_id or a bundle_id but not both'
        if not program_uuid and not course_id:
            error = 'You have to provide a course_id or bundle_id'
        if error:
            raise serializers.ValidationError(error)
        return attrs


class EdxappCoursePreEnrollmentQuerySerializer(EdxappCoursePreEnrollmentSerializer):
    """
    Handles the serialization of the context data required to create a course whitelisting
    on different backends
    """
    bundle_id = serializers.CharField(max_length=255, default=None)


def EdxappUserReadOnlySerializer(*args, **kwargs):   # pylint: disable=invalid-name
    """
    Fake class to lazily retrieve UserReadOnlySerializer
    """
    return get_user_read_only_serializer()(*args, **kwargs)
