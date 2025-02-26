import logging
from rest_framework.permissions import BasePermission
from rest_framework.authentication import get_authorization_header
from django.conf import settings

logger = logging.getLogger(__name__)


class DatacollectorPermission(BasePermission):
    """
    Permission class to allow access only if the request contains a valid GitHub Action token.
    """

    def has_permission(self, request, view):
        auth_header = get_authorization_header(request).decode('utf-8')
        auth_token = settings.EOX_CORE_DATA_COLLECT_AUTH_TOKEN
        if auth_header and auth_header == f"Bearer {auth_token}":
            return True
        return False
