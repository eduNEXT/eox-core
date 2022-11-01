"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_core.api.support.v1.permissions import EoxCoreSupportAPIPermission
from eox_core.api.support.v1.serializers import (
    OauthApplicationSerializer,
    WrittableEdxappRemoveUserSerializer,
    WrittableEdxappUsernameSerializer,
)
from eox_core.api.v1.serializers import EdxappUserReadOnlySerializer
from eox_core.api.v1.views import UserQueryMixin
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.comments_service_users import replace_username_cs_user
from eox_core.edxapp_wrapper.users import (
    create_edxapp_user,
    delete_edxapp_user,
    get_edxapp_user,
    get_user_signup_source,
)
from eox_core.utils import get_or_create_site_from_oauth_app_uris

User = get_user_model()
UserSignupSource = get_user_signup_source()  # pylint: disable=invalid-name

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

        message, status = delete_edxapp_user(**data)  # pylint: disable=redefined-outer-name

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


class OauthApplicationAPIView(UserQueryMixin, APIView):
    """
    Handles requests related to the
    django_oauth_toolkit Application object.
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreSupportAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @audit_drf_api(action='Generate Oauth Application.', method_name='eox_core_api_method')
    def post(self, request, *args, **kwargs):  # pylint: disable=too-many-locals
        """
        Creates a new Oauth Application from django_oauth_toolkit.

        This endpoint assumes that the URLs sent in the redirect_uris
        parameter are correct.

        In order to generate a valid application, this endpoint
        does multiple things:
        1 - Get or Create an edxapp user which will be the owner
        of the Application.
        2 - Grant permissions to the user that were sent in the
        "permissions" list.
        3 - Create User SignUp Source with the created user and the site
            sent in the redirect_uris field.
        4 - Create Application.

        Note: make sure to send the codenames of the permissions
        you want to grant to the user in the permissions list.
        Also, send the urls in the redirect_uris separated by
        simple whitespaces to avoid any errors during the creation.

        For example:

        **Requests**:
            POST <domain>/eox-core/support-api/v1/oauth-application/

        **Request body**:
        {
            "user": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "username": "johndoe",
                "permissions": ["can_call_eox_core", "can_call_eox_tenant"]
            },
            "redirect_uris": "http://testing-site.io/ http://testing-site.io",
            "client_type":"confidential",
            "authorization_grant_type":"client-credentials",
            "name": "test-application",
            "skip_authorization": true
        }

        **Response values**:
            - 200: Success, the Oauth Application has been created.
            - 400: Bad request, invalid request body format.
            - 500: The server has failed to get or create the.
            owner user for the application.
        """
        message = "Could not get or create edxapp User"

        serializer = OauthApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_creation_data = data.pop('user', {})
        user_permissions = user_creation_data.pop('permissions', [])
        site = get_or_create_site_from_oauth_app_uris(data.get('redirect_uris', ''))

        user_creation_data.update({
            'skip_extra_registration_fields': True,
            'activate_user': True,
            'skip_password': True,
            'site': site,
        })

        # Get or create user
        try:
            user = get_edxapp_user(**user_creation_data)
        except (NotFound, User.DoesNotExist):
            user, message = create_edxapp_user(**user_creation_data)

        if not user:
            LOG.error(message)

            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create SignUp Source in the Oauth Application site
        UserSignupSource.objects.get_or_create(user=user, site=site.name)

        # Grant permissions to user
        permissions = Permission.objects.filter(codename__in=user_permissions)
        user.user_permissions.add(*permissions)

        # Create Oauth Application
        data['user'] = user
        application, _ = Application.objects.get_or_create(**data)

        return Response(OauthApplicationSerializer(application).data, status=status.HTTP_200_OK)
