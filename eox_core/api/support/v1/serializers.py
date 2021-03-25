"""
Support API v1 serializers.
"""
# pylint: disable=abstract-method
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
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


class WrittableEdxappUsernameSerializer(serializers.Serializer):
    """
    Handles the serialization of the data required to update the username of an edxapp user.
    """
    new_username = serializers.CharField(max_length=USERNAME_MAX_LENGTH, write_only=True)

    def validate(self, attrs):
        """
        When a username update is being made, then it checks that:
            - The new username is not already taken by other user.
            - The user is not staff or superuser.
            - The user has just one signup source.
        """
        username = attrs.get("new_username")
        conflicts = check_edxapp_account_conflicts(None, username)
        if conflicts:
            raise serializers.ValidationError({"detail": "An account already exists with the provided username."})

        if self.instance.is_staff or self.instance.is_superuser:
            raise serializers.ValidationError({"detail": "You can't update users with roles like staff or superuser."})

        if UserSignupSource.objects.filter(user__email=self.instance.email).count() > MAX_SIGNUP_SOURCES_ALLOWED:
            raise serializers.ValidationError({"detail": "You can't update users with more than one sign up source."})

        return attrs

    def update(self, instance, validated_data):
        """
        Method to update username of edxapp User.
        """
        key = 'username'
        if validated_data:
            setattr(instance, key, validated_data['new_username'])
            instance.save()

        return instance
