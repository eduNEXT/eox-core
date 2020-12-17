"""
API v1 views.
"""

from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_core.api.v1.permissions import EoxCoreAPIPermission
from eox_core.api.v1.serializers import (
    EdxappCourseEnrollmentQuerySerializer,
    EdxappCourseEnrollmentSerializer,
    EdxappCoursePreEnrollmentSerializer,
    EdxappUserQuerySerializer,
    EdxappUserReadOnlySerializer,
    EdxappUserSerializer,
    WrittableEdxappUserSerializer,
)
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.enrollments import create_enrollment, delete_enrollment, get_enrollment, update_enrollment
from eox_core.edxapp_wrapper.pre_enrollments import (
    create_pre_enrollment,
    delete_pre_enrollment,
    get_pre_enrollment,
    update_pre_enrollment,
)
from eox_core.edxapp_wrapper.users import create_edxapp_user, get_edxapp_user

LOG = logging.getLogger(__name__)


class UserQueryMixin(object):
    """
    Provides tools to create user queries
    """
    def __init__(self, *args, **kwargs):
        """
        Defines instance attributes
        """
        super(UserQueryMixin, self).__init__(*args, **kwargs)
        self.query_params = None
        self.site = None

    def initial(self, request, *args, **kwargs):
        """
        Loads the site into the object for every kind of request.
        """
        super(UserQueryMixin, self).initial(request, *args, **kwargs)

        if hasattr(request, 'site'):
            self.site = request.site

    def get_query_params(self, request):
        """
        Utility to read the query params in a forgiving way
        As a side effect it loads self.query_params also in a forgiving way
        """
        query_params = request.query_params
        if not query_params and request.data:
            query_params = request.data

        self.query_params = query_params

        return query_params

    def get_user_query(self, request, query_params=None):
        """
        Utility to prepare the user query
        """
        if not query_params:
            query_params = self.get_query_params(request)

        username = query_params.get('username', None)
        email = query_params.get('email', None)

        if not email and not username:
            raise ValidationError(detail='Email or username needed')

        user_query = {}
        if hasattr(self, 'site') and self.site:
            user_query['site'] = self.site
        if username:
            user_query['username'] = username
        elif email:
            user_query['email'] = email

        return user_query


class EdxappUser(UserQueryMixin, APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
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
        Retrieve an user from edxapp
        """
        query = self.get_user_query(request)
        user = get_edxapp_user(**query)
        admin_fields = getattr(settings, 'ACCOUNT_VISIBILITY_CONFIGURATION', {}).get('admin_fields', {})
        serialized_user = EdxappUserReadOnlySerializer(user, custom_fields=admin_fields, context={'request': request})
        response_data = serialized_user.data
        # Show a warning if the request is providing email and username
        # to let the client know we're giving priority to the username
        if 'username' and 'email' in self.query_params:
            response_data['warning'] = 'The username prevails over the email when both are provided to get the user.'

        return Response(response_data)


class EdxappUserUpdater(UserQueryMixin, APIView):
    """
    Handles API requests to partially update users.
    """
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def patch(self, request, *args, **kwargs):
        """
        Partially update a user from edxapp. Not all the fields can be updated, just the ones thought as `safe`.

        For example:

        **Requests**:
            PATCH <domain>/eox-core/api/v1/user/

        **Request body**
            {
                "email"=<USER_EMAIL>,
                "is_active": true,
                "password": "new password"
            }

        **Response values**
            User serialized.
        """
        # Pop identification
        data = request.data.copy()
        query_params = {
            "email": data.pop("email", None),
        }
        query = self.get_user_query(request, query_params=query_params)
        user = get_edxapp_user(**query)

        serializer = WrittableEdxappUserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        admin_fields = getattr(settings, 'ACCOUNT_VISIBILITY_CONFIGURATION', {}).get('admin_fields', {})
        serialized_user = EdxappUserReadOnlySerializer(user, custom_fields=admin_fields, context={'request': request})
        return Response(serialized_user.data)


class EdxappEnrollment(UserQueryMixin, APIView):
    """
    Handles API requests to create users
    """
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def single_enrollment_create(self, *args, **kwargs):
        """
        Handle one create at the time
        """
        user_query = self.get_user_query(None, query_params=kwargs)
        user = get_edxapp_user(**user_query)

        enrollments, msgs = create_enrollment(user, **kwargs)
        # This logic block is needed to convert a single bundle_id enrollment in a list
        # of course_id enrollments which are appended to the response individually
        if not isinstance(enrollments, list):
            enrollments = [enrollments]
            msgs = [msgs]
        response_data = []
        for enrollment, msg in zip(enrollments, msgs):
            data = EdxappCourseEnrollmentSerializer(enrollment).data
            if msg:
                data["messages"] = msg
            response_data.append(data)

        return response_data

    def post(self, request, *args, **kwargs):
        """
        Handle creation of single or bulk enrollments
        """
        data = request.data
        return EdxappEnrollment.prepare_multiresponse(data, self.single_enrollment_create)

    def single_enrollment_update(self, *args, **kwargs):
        """
        Handle one update at the time
        """
        user_query = self.get_user_query(None, query_params=kwargs)
        user = get_edxapp_user(**user_query)

        course_id = kwargs.pop('course_id', None)
        if not course_id:
            raise ValidationError(detail='You have to provide a course_id for updates')
        mode = kwargs.pop('mode', None)

        return update_enrollment(user, course_id, mode, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Update enrollments on edxapp
        """
        data = request.data
        return EdxappEnrollment.prepare_multiresponse(data, self.single_enrollment_update)

    def get(self, request, *args, **kwargs):
        """
        Get enrollments on edxapp
        """
        user_query = self.get_user_query(request)
        user = get_edxapp_user(**user_query)

        course_id = self.query_params.get('course_id', None)

        if not course_id:
            raise ValidationError(detail='You have to provide a course_id')

        enrollment_query = {
            'username': user.username,
            'course_id': course_id,
        }
        enrollment, errors = get_enrollment(**enrollment_query)

        if errors:
            raise NotFound(detail=errors)
        response = EdxappCourseEnrollmentSerializer(enrollment).data
        return Response(response)

    def delete(self, request, *args, **kwargs):
        """
        Delete enrollment on edxapp
        """
        user_query = self.get_user_query(request)
        user = get_edxapp_user(**user_query)

        course_id = self.query_params.get('course_id', None)

        if not course_id:
            raise ValidationError(detail='You have to provide a course_id')

        delete_enrollment(user=user, course_id=course_id)
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
        errors_in_bulk_response = False
        many = isinstance(request_data, list)
        serializer = EdxappCourseEnrollmentQuerySerializer(data=request_data, many=many)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not isinstance(data, list):
            data = [data]

        for enrollment_query in data:

            try:
                result = action_method(**enrollment_query)
                # The result can be a list if the enrollment was in a bundle
                if isinstance(result, list):
                    multiple_responses += result
                else:
                    multiple_responses.append(result)
            except APIException as error:
                errors_in_bulk_response = True
                enrollment_query["error"] = {
                    "detail": error.detail,
                }
                multiple_responses.append(enrollment_query)

        if many or 'bundle_id' in request_data:
            response = multiple_responses
        else:
            response = multiple_responses[0]

        response_status = status.HTTP_200_OK
        if errors_in_bulk_response:
            response_status = status.HTTP_202_ACCEPTED
        return Response(response, status=response_status)

    def handle_exception(self, exc):
        """
        Handle exception: log it
        """
        if isinstance(exc, APIException):
            LOG.error('API Error: %s', repr(exc.detail))

        return super(EdxappEnrollment, self).handle_exception(exc)


class EdxappPreEnrollment(APIView):
    """
    Handles API requests to manage whitelistings (pre-enrollments)
    """
    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, *args, **kwargs):
        """
        Create whitelistings on edxapp
        """
        serializer = EdxappCoursePreEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course_id = data.pop('course_id', None)
        pre_enrollment, warning = create_pre_enrollment(course_id=course_id, **data)
        response_data = EdxappCoursePreEnrollmentSerializer(pre_enrollment, context=warning).data
        return Response(response_data)

    def put(self, request, *args, **kwargs):
        """
        Update whitelistings on edxapp
        """
        serializer = EdxappCoursePreEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data.get('email')
        course_id = data.get('course_id')
        auto_enroll = data.pop('auto_enroll', False)

        pre_enrollment_query = {
            'email': email,
            'course_id': course_id,
        }

        pre_enrollment = get_pre_enrollment(**pre_enrollment_query)
        update_query = {
            'pre_enrollment': pre_enrollment,
            'auto_enroll': auto_enroll,
        }
        updated_pre_enrollment = update_pre_enrollment(**update_query)
        response = EdxappCoursePreEnrollmentSerializer(updated_pre_enrollment).data
        return Response(response)

    def delete(self, request, *args, **kwargs):
        """
        Delete whitelistings on edxapp
        """
        query_params = request.query_params
        if not query_params:
            query_params = request.data

        serializer = EdxappCoursePreEnrollmentSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data.get('email')
        course_id = data.get('course_id')

        pre_enrollment_query = {
            'email': email,
            'course_id': course_id,
        }

        pre_enrollment = get_pre_enrollment(**pre_enrollment_query)
        delete_query = {
            'pre_enrollment': pre_enrollment,
        }
        delete_pre_enrollment(**delete_query)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        """
        Get whitelistings on edxapp
        """
        query_params = request.query_params
        if not query_params:
            query_params = request.data

        serializer = EdxappCoursePreEnrollmentSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        pre_enrollment = get_pre_enrollment(**data)
        response = EdxappCoursePreEnrollmentSerializer(pre_enrollment).data
        return Response(response)

    def handle_exception(self, exc):
        """
        Handle exception: log it
        """
        data = self.request.data or self.request.query_params
        self.log('API Error', data, exc)
        return super(EdxappPreEnrollment, self).handle_exception(exc)

    def log(self, desc, data, exception=None):
        """
        log util for this view
        """
        log_data = []
        log_data.append(desc)
        log_data.append('Exception:')
        if isinstance(exception, APIException):
            log_data.append(repr(exception.detail))
        else:
            log_data.append(repr(exception))

        log_data.append('Request data:')
        if not data:
            log_data.append('Empty request')
        else:
            for key, value in data.items():
                log_data.append("{}: {}".format(key, value))

        LOG.error(' '.join(log_data))


class UserInfo(APIView):
    """
    Auth-only view to check some basic info about the current user
    Can use Oauth2/Session
    """
    authentication_classes = (BearerAuthentication, SessionAuthentication)
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
            'auth': six.text_type(request.auth)
        }

        if request.user.is_staff:
            content['is_superuser'] = request.user.is_superuser
            content['is_staff'] = request.user.is_staff

        return Response(content)
