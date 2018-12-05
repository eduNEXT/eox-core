"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from rest_framework_oauth.authentication import OAuth2Authentication
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six
from eox_core.api.v1.serializers import (
    EdxappUserQuerySerializer,
    EdxappUserSerializer,
    EdxappCourseEnrollmentSerializer,
    EdxappCourseEnrollmentQuerySerializer,
    EdxappUserReadOnlySerializer
)
from eox_core.edxapp_wrapper.users import create_edxapp_user, get_edxapp_user
from eox_core.edxapp_wrapper.enrollments import create_enrollment


LOG = logging.getLogger(__name__)


class EdxappUser(APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, *args, **kwargs):
        """
        Creates the users on edxapp
        """
        serializer = EdxappUserQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data['site'] = get_current_site(request)
        user, msg = create_edxapp_user(**data)

        serialized_user = EdxappUserSerializer(user)
        response_data = serialized_user.data
        if msg:
            response_data["messages"] = msg
        return Response(response_data)

    def get(self, request, *args, **kwargs):
        """
        Creates the users on edxapp
        """
        query = {key: request.GET[key] for key in ['username', 'email'] if key in request.GET}
        query['site'] = get_current_site(request)
        user = get_edxapp_user(**query)
        serialized_user = EdxappUserReadOnlySerializer(user, context={'request': request})
        response_data = serialized_user.data

        return Response(response_data)


class EdxappEnrollment(APIView):
    """
    Handles API requests to create users
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    # pylint: disable=too-many-locals
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

        for enrollment_request in data:
            enrollments, msgs = create_enrollment(**enrollment_request)
            if not isinstance(enrollments, list):
                enrollments = [enrollments]
                msgs = [msgs]
            for enrollment, msg in zip(enrollments, msgs):
                response_data = EdxappCourseEnrollmentSerializer(enrollment).data
                if msg:
                    response_data["messages"] = msg
                multiple_responses.append(response_data)

        if many or 'bundle_id' in request.data:
            response = multiple_responses
        else:
            response = multiple_responses[0]
        return Response(response)

    def handle_exception(self, exc):
        """
        Handle exception: log it
        """
        self.log('API Error', self.kwargs, exc)
        return super(EdxappEnrollment, self).handle_exception(exc)

    def log(self, desc, data, exception=None):
        """
        log util for this view
        """
        username = data.get('username')
        bundle_id = data.get('bundle_id')
        course_id = data.get('course_id')
        mode = data.get('mode')
        is_active = data.get('is_active')
        force = data.get('force')
        id_val = bundle_id or course_id
        id_str = 'bundle_id' if bundle_id else 'course_id'
        logstr = id_str + ': %s, username: %s, mode: %s, is_active: %s, force: %s'
        logarr = [id_val, username, mode, is_active, force]
        if exception:
            LOG.warn(desc + ': Exception %s,' + logstr, repr(exception), *logarr)
        else:
            LOG.info(desc + ': ' + logstr, *logarr)


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAdminUser,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        """
        handle GET request
        """
        content = {
            # `django.contrib.auth.User` instance.
            'user': six.text_type(request.user.username),
            'email': six.text_type(request.user.email),
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'auth': six.text_type(request.auth)
        }
        return Response(content)
