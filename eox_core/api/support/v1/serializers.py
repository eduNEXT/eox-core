"""
Support API v1 serializers.
"""
# pylint: disable=abstract-method
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from rest_framework import serializers


class WrittableEdxappRemoveUserSerializer(serializers.Serializer):
    """
    Handles the serialization when a user is being removed.
    """
    case_id = serializers.CharField(write_only=True, default=timezone.now().strftime('%Y%m%d%H%M%S'))
    is_support_user = serializers.BooleanField(default=True)
