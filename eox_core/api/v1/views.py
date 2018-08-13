"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_oauth.authentication import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from eox_core.api.v1.serializers import EdxappUserQuerySerializer, EdxappUserSerializer, EdxappCourseEnrollmentSerializer, EdxappCourseEnrollmentQuerySerializer
from eox_core.edxapp_wrapper.users import create_edxapp_user
from eox_core.edxapp_wrapper.enrollments import create_enrollment
from django.utils import six


class EdxappUser(APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (OAuth2Authentication, JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

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


class EdxappEnrollment(APIView):
    """
    Handles API requests to create users
    """
    authentication_classes = (OAuth2Authentication, JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, *args, **kwargs):
        """
        Creates the users on edxapp
        """
        multiple_responses = []
        many = isinstance(request.data, list)
        serializer = EdxappCourseEnrollmentQuerySerializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not isinstance(data, list):
            data = [data]

        for one in data:
            enrollment, msg = create_enrollment(**one)
            serialized_enrollment = EdxappCourseEnrollmentSerializer(enrollment)
            response_data = serialized_enrollment.data
            if msg:
                response_data["messages"] = msg
            multiple_responses.append(response_data)

        if many:
            return Response(multiple_responses)
        else:
            return Response(multiple_responses[0])


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session/JWT authentication
    """
    authentication_classes = (OAuth2Authentication, JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

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
