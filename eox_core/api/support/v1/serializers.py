"""
Support API v1 serializers.
"""
# pylint: disable=abstract-method
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from oauth2_provider.models import Application
from rest_framework import serializers

from eox_core.api.v1.serializers import MAX_SIGNUP_SOURCES_ALLOWED
from eox_core.edxapp_wrapper.users import (
    check_edxapp_account_conflicts,
    get_user_signup_source,
    get_username_max_length,
)

UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name

USERNAME_MAX_LENGTH = get_username_max_length()


class WrittableEdxappRemoveUserSerializer(serializers.Serializer):
    """
    Handles the serialization when a user is being removed.
    """
    case_id = serializers.CharField(write_only=True, default=timezone.now().strftime('%Y%m%d%H%M%S'))
    is_support_user = serializers.BooleanField(default=True)


class WrittableEdxappUserSerializer(serializers.Serializer):
    """
    Base serializer for updating username or email of an edxapp user.

    When a username/email update is being made the following validations are performed:
    - The new username/email is not already taken by another user.
    - The user is not staff or superuser.
    - The user has just one signup source.
    """

    def validate_conflicts(self, attrs):
        """
        Validates that no conflicts exist for the provided username or email.
        """
        username = attrs.get("new_username")
        email = attrs.get("new_email")

        conflicts = check_edxapp_account_conflicts(email, username)
        if conflicts:
            raise serializers.ValidationError({"detail": "An account already exists with the provided username or email."})

        return attrs

    def validate_role_restrictions(self, attrs):
        """
        Validates that the user is not staff or superuser and has just one signup source.
        """
        if self.instance.is_staff or self.instance.is_superuser:
            raise serializers.ValidationError({"detail": "You can't update users with roles like staff or superuser."})

        if UserSignupSource.objects.filter(user__email=self.instance.email).count() > MAX_SIGNUP_SOURCES_ALLOWED:
            raise serializers.ValidationError({"detail": "You can't update users with more than one sign up source."})

        return attrs

    def validate(self, attrs):
        """
        Base validate method to be used by child serializers to validate common restrictions.
        """
        self.validate_conflicts(attrs)
        self.validate_role_restrictions(attrs)

        return attrs


class WrittableEdxappUsernameSerializer(WrittableEdxappUserSerializer):
    """
    Handles the serialization of the data required to update the username of an edxapp user.
    """

    new_username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        allow_blank=False,
        allow_null=False,
    )

    def update(self, instance, validated_data):
        """
        Updates the username of the edxapp User.
        """
        instance.username = validated_data["new_username"]
        instance.save()
        return instance


class WrittableEdxappEmailSerializer(WrittableEdxappUserSerializer):
    """
    Handles the serialization of the data required to update the email of an edxapp user.
    """

    new_email = serializers.EmailField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )

    def update(self, instance, validated_data):
        """
        Updates the email of the edxapp User.
        """
        instance.email = validated_data["new_email"]
        instance.save()
        return instance

class OauthApplicationUserSerializer(serializers.Serializer):
    """
    Oauth Application owner serializer.
    """
    email = serializers.EmailField()
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    fullname = serializers.CharField(max_length=255, write_only=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
        write_only=True,
        required=False,
    )


class OauthApplicationSerializer(serializers.ModelSerializer):
    """
    Oauth Application model serializer.
    """
    user = OauthApplicationUserSerializer()

    class Meta:
        """Meta class."""
        model = Application
        read_only_fields = ('created', 'updated', )
        fields = '__all__'
