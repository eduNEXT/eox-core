"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_oauth.authentication import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny
from eox_core.api.v1.serializers import EdxappUserQuerySerializer, EdxappUserSerializer
from eox_core.edxapp_wrapper.users import create_edxapp_user
from django.utils import six


class EdxappUser(generics.CreateAPIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (BasicAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        Creates the users on edxapp
        """
        serializer = EdxappUserQuerySerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)

        user, msg = create_edxapp_user(**serializer.validated_data)

        serialized_user = EdxappUserSerializer(user)
        response_data = serialized_user.data
        if msg:
            response_data["messages"] = msg
        return Response(response_data)


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session/JWT authentication
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication, JSONWebTokenAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer)

    def get(self, request, format=None):
        content = {
            # `django.contrib.auth.User` instance.
            'user': six.text_type(request.user.username),
            'email': six.text_type(request.user.email),
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'auth': six.text_type(request.auth)
        }
        return Response(content)
