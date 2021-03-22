"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

import logging

from django.contrib.sites.shortcuts import get_current_site
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_core.api.support.v1.permissions import EoxCoreSupportAPIPermission
from eox_core.api.support.v1.serializers import WrittableEdxappRemoveUserSerializer
from eox_core.api.v1.views import UserQueryMixin
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.users import delete_edxapp_user, get_edxapp_user

LOG = logging.getLogger(__name__)


class EdxappUser(UserQueryMixin, APIView):
    """
    Handles API requests to remove users
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreSupportAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def delete(self, request, *args, **kwargs):  # pylint: disable=too-many-locals
        """
        Allows to safely remove an edxapp User.

        For example:

        **Requests**:
            DELETE <domain>/eox-core/api/v1/remove-user/

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
