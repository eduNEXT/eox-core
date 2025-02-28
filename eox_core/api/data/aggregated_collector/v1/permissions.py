"""
Custom permission classes for the Aggregated Collector API.
"""

import logging

from django.conf import settings
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class AggregatedCollectorPermission(BasePermission):
    """
    Permission class to allow access only if:
    - The AGGREGATED_DATA_COLLECTOR_API_ENABLED setting is True.
    - The request contains a valid GitHub Action token.
    """

    def has_permission(self, request, view):
        # Check if the API is enabled
        if not getattr(settings, "AGGREGATED_DATA_COLLECTOR_API_ENABLED", False):
            return False

        # Check if the request contains a valid token
        auth_header = get_authorization_header(request).decode('utf-8')
        auth_token = settings.EOX_CORE_AGGREGATED_COLLECTOR_AUTH_TOKEN
        if auth_header and auth_header == f"Bearer {auth_token}":
            return True
        return False
