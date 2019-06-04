"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals
import logging

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError, NotFound, APIException
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import status

from rest_framework_oauth.authentication import OAuth2Authentication
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six
from django.conf import settings
from eox_core.api.v1.permissions import EoxCoreAPIPermission
from eox_core.api.v1.serializers import (
    EdxappUserQuerySerializer,
    EdxappUserSerializer,
    EdxappCourseEnrollmentSerializer,
    EdxappCourseEnrollmentQuerySerializer,
    EdxappUserReadOnlySerializer,
)
from eox_core.edxapp_wrapper.users import create_edxapp_user, get_edxapp_user
from eox_core.edxapp_wrapper.enrollments import (
    create_enrollment,
    update_enrollment,
    get_enrollment,
    delete_enrollment,
)


LOG = logging.getLogger(__name__)


class EdxappUser(APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
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
        Retrieves an user from edxapp
        """
        query = {key: request.GET[key] for key in ['username', 'email'] if key in request.GET}
        query['site'] = get_current_site(request)
        user = get_edxapp_user(**query)
        admin_fields = getattr(settings, 'ACCOUNT_VISIBILITY_CONFIGURATION', {}).get('admin_fields', {})
        serialized_user = EdxappUserReadOnlySerializer(user, custom_fields=admin_fields, context={'request': request})
        response_data = serialized_user.data

        return Response(response_data)


class EdxappEnrollment(APIView):
    """
    Handles API requests to create users
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    # pylint: disable=too-many-locals
    def post(self, request, *args, **kwargs):
        """
        Creates the users on edxapp
        """
        data = dict(request.data)
        return EdxappEnrollment.prepare_multiresponse(data, create_enrollment)

    def put(self, request, *args, **kwargs):
        """
        Update enrollments on edxapp
        """
        data = dict(request.data)
        return EdxappEnrollment.prepare_multiresponse(data, update_enrollment)

    def get(self, request, *args, **kwargs):
        """
        Get enrollments on edxapp
        """
        data = dict(request.data)
        course_id = data.get('course_id', None)
        username = data.get('username', None)
        email = data.get('email', None)

        if not course_id:
            return Response('You have to provide a course_id', status.HTTP_400_BAD_REQUEST)
        if not email and not username:
            return Response('Email or username needed', status.HTTP_400_BAD_REQUEST)
        enrollment, errors = get_enrollment(**data)
        if errors:
            return Response(errors, status.HTTP_404_NOT_FOUND)
        response = EdxappCourseEnrollmentSerializer(enrollment).data
        return  Response(response)

    def delete(self, request, *args, **kwargs):
        """
        Delete enrollment on edxapp
        """
        data = dict(request.data)
        delete_enrollment(**data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def prepare_multiresponse(request_data, action_method):
        """
        Prepare a multiple part response according to the request_data and the action_method provided
        Args:
            request_data: Data dictionary containing the query o queries to be processed
            action_method: Function to be applied to the queries (create, update)

        Returns: List of responses
        """
        multiple_responses = []
        many = isinstance(request_data, list)
        serializer = EdxappCourseEnrollmentQuerySerializer(data=request_data, many=many)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not isinstance(data, list):
            data = [data]

        for enrollment_query in data:
            enrollments, msgs = action_method(**enrollment_query)
            if not isinstance(enrollments, list):
                enrollments = [enrollments]
                msgs = [msgs]
            for enrollment, msg in zip(enrollments, msgs):
                response_data = EdxappCourseEnrollmentSerializer(enrollment).data
                if msg:
                    response_data["messages"] = msg
                multiple_responses.append(response_data)

        if many or 'bundle_id' in request_data:
            response = multiple_responses
        else:
            response = multiple_responses[0]
        return Response(response)

    def handle_exception(self, exc):
        """
        Handle exception: log it
        """
        if isinstance(exc, APIException):
            LOG.error('API Error: %s', repr(exc.detail))

        return super(EdxappEnrollment, self).handle_exception(exc)


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
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
