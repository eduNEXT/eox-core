"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_core.api.support.v1.permissions import EoxCoreSupportAPIPermission
from eox_core.api.support.v1.serializers import WrittableEdxappRemoveUserSerializer, WrittableEdxappUsernameSerializer
from eox_core.api.v1.serializers import EdxappUserReadOnlySerializer
from eox_core.api.v1.views import UserQueryMixin
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.comments_service_users import replace_username_cs_user
from eox_core.edxapp_wrapper.users import delete_edxapp_user, get_edxapp_user

try:
    from eox_audit_model.decorators import audit_drf_api
except ImportError:
    def audit_drf_api(*args, **kwargs):
        """Identity decorator"""
        return lambda x: x

LOG = logging.getLogger(__name__)


class EdxappUser(UserQueryMixin, APIView):
    """
    Handles API requests to remove users
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreSupportAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @audit_drf_api(action='Remove edxapp User.', method_name='eox_core_api_method')
    def delete(self, request, *args, **kwargs):  # pylint: disable=too-many-locals
        """
        Allows to safely remove an edxapp User.

        For example:

        **Requests**:
            DELETE <domain>/eox-core/support-api/v1/user/

        **Request body**:
            {
                "case_id": Optional. ID of the support case for naming the retired user Email
            }

        **Response values**:
            - 200: Success, user has multiple signup sources and the one that matches the current site
                    has been deleted.
            - 202: Success, user has a unique signup source and has been safely removed from the platform.
            - 400: Bad request, invalid case_id or user has no signup source on the request site.
        """
        query = self.get_user_query(request)

        serializer = WrittableEdxappRemoveUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["site"] = get_current_site(request)
        data["user"] = get_edxapp_user(**query)

        message, status = delete_edxapp_user(**data)

        return Response(message, status=status)


class EdxappReplaceUsername(UserQueryMixin, APIView):
    """
    Handles the replacement of the username.
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreSupportAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @audit_drf_api(action="Update an Edxapp user's Username.", method_name='eox_core_api_method')
    def patch(self, request, *args, **kwargs):
        """
        Allows to safely update an Edxapp user's Username along with the
        forum associated User.

        For now users that have different signup sources cannot be updated.

        For example:

        **Requests**:
            PATCH <domain>/eox-core/support-api/v1/replace-username/

        **Request body**
            {
                "new_username": "new username"
            }

        **Response values**
            User serialized.
        """
        query = self.get_user_query(request)
        user = get_edxapp_user(**query)
        data = request.data

        with transaction.atomic():
            serializer = WrittableEdxappUsernameSerializer(user, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            data = serializer.validated_data
            data["user"] = user

            # Update user in cs_comments_service forums
            replace_username_cs_user(**data)

        admin_fields = getattr(settings, "ACCOUNT_VISIBILITY_CONFIGURATION", {}).get(
            "admin_fields", {}
        )
        serialized_user = EdxappUserReadOnlySerializer(
            user, custom_fields=admin_fields, context={"request": request}
        )
        return Response(serialized_user.data)
