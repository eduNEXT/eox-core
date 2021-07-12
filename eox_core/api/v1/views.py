"""
API v1 views.
"""

# pylint: disable=too-many-lines
from __future__ import absolute_import, unicode_literals

import logging

import edx_api_doc_tools as apidocs
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
    EdxappGradeSerializer,
    EdxappUserQuerySerializer,
    EdxappUserReadOnlySerializer,
    EdxappUserSerializer,
    WrittableEdxappUserSerializer,
)
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from eox_core.edxapp_wrapper.coursekey import get_valid_course_key
from eox_core.edxapp_wrapper.courseware import get_courseware_courses
from eox_core.edxapp_wrapper.enrollments import create_enrollment, delete_enrollment, get_enrollment, update_enrollment
from eox_core.edxapp_wrapper.grades import get_course_grade_factory
from eox_core.edxapp_wrapper.pre_enrollments import (
    create_pre_enrollment,
    delete_pre_enrollment,
    get_pre_enrollment,
    update_pre_enrollment,
)
from eox_core.edxapp_wrapper.users import create_edxapp_user, get_edxapp_user, get_user_read_only_serializer

try:
    from eox_audit_model.decorators import audit_drf_api
except ImportError:
    def audit_drf_api(*args, **kwargs):
        """Identity decorator"""
        return lambda x: x

LOG = logging.getLogger(__name__)


class UserQueryMixin:
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

        if hasattr(request, "site"):
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

        username = query_params.get("username", None)
        email = query_params.get("email", None)

        if not email and not username:
            raise ValidationError(detail="Email or username needed")

        user_query = {}
        if hasattr(self, "site") and self.site:
            user_query["site"] = self.site
        if username:
            user_query["username"] = username
        elif email:
            user_query["email"] = email

        return user_query


class EdxappUser(UserQueryMixin, APIView):
    """
    Handles the creation of a User on edxapp

    **Example Requests**

        POST /eox-core/api/v1/user/

        Request data: {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "fullname": "John Doe",
            "password": "p@ssword",
        }

    The extra registration fields configured for the microsite, should be sent along with the rest of the parameters.
    These extra fields would be required depending on the settings.
    For example, if we have the microsite settings:

        "EDNX_CUSTOM_REGISTRATION_FIELDS": [
            {
                "label": "Personal ID",
                "name": "personal_id",
                "type": "text"
            },
        ],

        "REGISTRATION_EXTRA_FIELDS": {
            "gender": "required",
            "country": "hidden",
            "personal_id": "required",
        },

        "extended_profile_fields": [
            "personal_id",
        ],

    Then a request to create a user should look like this:

        {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "fullname": "John Doe",
            "password": "p@ssword",
            "gender": "m",
            "country": "GR",
            "personal_id": "12345",
        }

    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @apidocs.schema(
        body=EdxappUserQuerySerializer,
        responses={
            200: EdxappUserSerializer,
            400: "Bad request, a required field is missing or has been entered with the wrong format.",
            401: "Unauthorized user to make the request.",
        },
    )
    @audit_drf_api(
        action="Create edxapp user",
        data_filter=[
            "email",
            "username",
            "fullname",
        ],
        hidden_fields=["password"],
        method_name='eox_core_api_method',
    )
    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a User on edxapp

        **Example Requests**

            POST /eox-core/api/v1/user/

            Request data: {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "fullname": "John Doe",
                "password": "p@ssword",
            }

        **Parameters**

        - `username` (**required**, string, _body_):
            The username to be assigned to the new user.

        - `email` (**required**, string, _body_):
            The email to be assigned to the new user.

        - `password` (**required**, string, _body_):
            The password of the new user. If `skip_password` is True, this field will be omitted.

        - `fullname` (**required**, string, _body_):
            The full name to be assigned.

        - `activate_user` (**optional**, boolean, default=False, _body_):
            Flag indicating whether the user is active.

        - `skip_password` (**optional**, boolean, default=False, _body_):
            Flag indicating whether the password should be omitted.

        If you have extra registration fields configured in your settings or extended_profile fields, you can send them with the rest of the parameters.
        These extra fields would be required depending on the site settings.
        For example:

            {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "fullname": "John Doe",
                "password": "p@ssword",
                "gender": "m",
                "country": "GR",
            }


        **Returns**

        - 200: Success, user created.
        - 400: Bad request, a required field is missing or has been entered with the wrong format, or the chosen email/username already belongs to a user.
        - 401: Unauthorized user to make the request.
        """
        serializer = EdxappUserQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["site"] = get_current_site(request)
        user, msg = create_edxapp_user(**data)

        serialized_user = EdxappUserSerializer(user)
        response_data = serialized_user.data
        if msg:
            response_data["messages"] = msg
        return Response(response_data)

    @apidocs.schema(
        parameters=[
            apidocs.query_parameter(
                name="username",
                param_type=str,
                description="**required**, The username used to identify the user. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="email",
                param_type=str,
                description="**required**, The email used to identify the user. Use either username or email.",
            ),
        ],
        responses={
            200: get_user_read_only_serializer(),
            400: "Bad request, missing email or username",
            401: "Unauthorized user to make the request.",
            404: "User not found",
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieves information about an edxapp user,
        given an email or a username.

        The username prevails over the email when both are provided to get the user.

        **Example Requests**

            GET /eox-core/api/v1/user/?username=johndoe

            Query parameters: {
              "username": "johndoe",
            }

        **Response details**

        - `username (str)`: Username of the edxapp user
        - `is_active (str)`: Indicates if the user is active on the platform
        - `email (str)`: Email of the user
        - `gender (str)`: Gender of the user
        - `date_joined (str)`: Date for when the user was registered in the platform
        - `name (str)`: Fullname of the user
        - `country (str)`: Country of the user
        - `level_of_education (str)`: Level of education of the user
        - `year_of_birth (int)`: Year of birth of the user
        - `bio (str)`: Bio of the user
        - `goals (str)`: Goals of the user
        - `extended_profile (list)`: List of dictionaries that contains the user-profile meta fields
            - `field_name (str)`: Name of the extended profile field
            - `field_value (str)`: Value of the extended profile field
        - `mailing_address (str)`
        - `social_links (List)`: List that contains the social links of the user, if any.
        - `account_privacy (str)`: Indicates the account privacy type
        - `state (str)`: State (only for US)
        - `secondary_email (str)`: Secondary email of the user
        - `profile_image (dictionary)`:
            - `has_image (Bool)`: Indicates if user has profile image
            - `image_url_medium (str)`: Url of the profile image in medium size
            - `image_url_small (str)`: Url of the profile image in small size
            - `image_url_full (str)`: Url of the profile image in full size,
            - `image_url_large (str)`: Url of the profile image in large size
        - `secondary_email_enabled (Bool)`: Indicates if the secondary email is enable
        - `phone_number (str)`: Phone number of the user
        - `requires_parental_consent (Bool)`: Indicates whether parental consent is required for the user

        **Returns**

        - 200: Success, user found.
        - 400: Bad request, missing either email or username
        - 401: Unauthorized user to make the request.
        - 404: User not found
        """
        query = self.get_user_query(request)
        user = get_edxapp_user(**query)
        admin_fields = getattr(settings, "ACCOUNT_VISIBILITY_CONFIGURATION", {}).get(
            "admin_fields", {}
        )
        serialized_user = EdxappUserReadOnlySerializer(
            user, custom_fields=admin_fields, context={"request": request}
        )
        response_data = serialized_user.data
        # Show a warning if the request is providing email and username
        # to let the client know we're giving priority to the username
        if "username" and "email" in self.query_params:
            response_data[
                "warning"
            ] = "The username prevails over the email when both are provided to get the user."

        return Response(response_data)


class EdxappUserUpdater(UserQueryMixin, APIView):
    """
    Partially updates a user from edxapp.

    Not all the fields can be updated, just the ones thought as `safe`. By default, this fields are the ones defined in the
    EOX_CORE_USER_UPDATE_SAFE_FIELDS

    **Example Requests**

        PATCH /eox-core/api/v1/update-user/

        Request data: {
            "email": "johndoe@example.com",
            "fullname": "John Doe R",
            "password": "new-p@ssword",
        }

    The extra registration fields configured for the microsite, should be sent along with the rest of the parameters.
    These extra fields would be required (their value cannot be changed to null) depending on the settings.

    For example, if we have the microsite settings:

        "EDNX_CUSTOM_REGISTRATION_FIELDS": [
            {
                "label": "Personal ID",
                "name": "personal_id",
                "type": "text"
            },
        ],

        "REGISTRATION_EXTRA_FIELDS": {
            "gender": "required",
            "country": "hidden",
            "personal_id": "required",
        },

        "extended_profile_fields": [
            "personal_id",
        ],

    Then a request to create a user should look like this:

        {
            "email": "johndoe@example.com",
            "fullname": "John Doe R",
            "password": "new-p@ssword",
            "country": "CO",
            "personal_id": "00099",
        }
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @apidocs.schema(
        body=WrittableEdxappUserSerializer,
        responses={
            200: get_user_read_only_serializer(),
            400: "Bad request, a required field is now null or has been entered with the wrong format.",
            401: "Unauthorized user to make the request.",
            404: "User not found.",
        },
    )
    @audit_drf_api(
        action='Partially update a user from edxapp',
        data_filter=[
            'email',
            'is_active',
        ],
        hidden_fields=['password'],
        method_name='eox_core_api_method',
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially updates a user from edxapp.

        **Example Requests**

            PATCH /eox-core/api/v1/update-user/

            Request data: {
                "email": "johndoe@example.com",
                "fullname": "John Doe R",
                "password": "new-p@ssword",
            }


        **Parameters**

        - `email` (**required**, string, _body_):
            The email used to identify the user. Use either username or email.

        - `username` (**required**, string, _body_):
            The username used to identify the user. Use either username or email.

        - `password` (**optional**, string, _body_):
            The new password of the user.

        - `fullname` (**optional**, string, _body_):
            The full name to be assigned.

        - `is_active` (**optional**, boolean, _body_):
            Flag indicating if the user is active on the platform.

        - Not all the fields can be updated, just the ones thought as 'safe', such as: "is_active", "password", "fullname"

        - By default, these are the 'safe' extra registration fields: "mailing_address", "year_of_birth", "gender", "level_of_education",
        "city", "country", "goals", "bio" and "phone_number".

        If you have extra registration fields configured in your settings or extended_profile fields, and you want to update them, you can send them along with the rest of the parameters.
        For example:

            {
                "email": "johndoe@example.com",
                "fullname": "John Doe R",
                "password": "new-p@ssword",
                "gender": "f",
                "country": "US",
            }

        **Response details**

        - `username (str)`: Username of the edxapp user
        - `is_active (str)`: Indicates if the user is active on the platform
        - `email (str)`: Email of the user
        - `gender (str)`: Gender of the user
        - `date_joined (str)`: Date for when the user was registered in the platform
        - `name (str)`: Fullname of the user
        - `country (str)`: Country of the user
        - `level_of_education (str)`: Level of education of the user
        - `year_of_birth (int)`: Year of birth of the user
        - `bio (str)`: Bio of the user
        - `goals (str)`: Goals of the user
        - `extended_profile (list)`: List of dictionaries that contains the user-profile meta fields
            - `field_name (str)`: Name of the extended profile field
            - `field_value (str)`: Value of the extended profile field
        - `mailing_address (str)`
        - `social_links (List)`: List that contains the social links of the user, if any.
        - `account_privacy (str)`: Indicates the account privacy type
        - `state (str)`: State (only for US)
        - `secondary_email (str)`: Secondary email of the user
        - `profile_image (dictionary)`:
            - `has_image (Bool)`: Indicates if user has profile image
            - `image_url_medium (str)`: Url of the profile image in medium size
            - `image_url_small (str)`: Url of the profile image in small size
            - `image_url_full (str)`: Url of the profile image in full size,
            - `image_url_large (str)`: Url of the profile image in large size
        - `secondary_email_enabled (Bool)`: Indicates if the secondary email is enable
        - `phone_number (str)`: Phone number of the user
        - `requires_parental_consent (Bool)`: Indicates whether parental consent is required for the user

        **Returns**

        - 200: Success, user updated.
        - 400: Bad request, a required field is now null or has been entered with the wrong format.
        - 401: Unauthorized user to make the request.
        - 404: User not found
        """
        # Pop identification
        data = request.data.copy()
        query_params = {
            "email": data.pop("email", None),
            "username": data.pop("username", None),
        }
        query = self.get_user_query(request, query_params=query_params)
        user = get_edxapp_user(**query)

        serializer = WrittableEdxappUserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        admin_fields = getattr(settings, "ACCOUNT_VISIBILITY_CONFIGURATION", {}).get(
            "admin_fields", {}
        )
        serialized_user = EdxappUserReadOnlySerializer(
            user, custom_fields=admin_fields, context={"request": request}
        )
        return Response(serialized_user.data)


class EdxappEnrollment(UserQueryMixin, APIView):
    """
    Handles API requests to create users
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @apidocs.schema(
        body=EdxappCourseEnrollmentSerializer,
        responses={
            200: EdxappCourseEnrollmentSerializer,
            202: "User doesn't belong to site.",
            400: "Bad request, invalid course_id or missing either email or username.",
        },
    )
    @audit_drf_api(action='Create single or bulk enrollments', method_name='eox_core_api_method')
    def post(self, request, *args, **kwargs):
        """
        Handle creation of single or bulk enrollments

        **Example Requests**

            POST /eox-core/api/v1/enrollment/

            Request data: {
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
              "mode": "audit",
              "is_active": "False",
              "enrollment_attributes": [
                {
                  "namespace": "credit",
                  "name": "provider_id",
                  "value": "institution_name"
                }
              ]
            }

        **Parameters**

        - `username` (**required**, string, _body_):
            The username used to identify the user you want to enroll.  Use either username or email.

        - `email` (**required**, string, _body_):
            The email used to identify the user you to enroll.  Use either username or email.

        - `course_id` (**required**, string, _body_):
            The id of the course in which you want to enroll the user.

        - `mode` (**required**, string, _body_):
            The course mode for the enrollment.  Must be available for the course.

        - `is_active` (boolean, _body_):
            Flag indicating whether the enrollment is active.

        - `enrollment_attributes` (list, _body_):
            List of enrollment attributes. An enrollment attribute can be used to add extra parameters for a specific course mode.
            It must be a dictionary containing the following:
            - namespace: namespace of the attribute
            - name: name of the attribute
            - value: value of the attribute

        In case the case of bulk enrollments, you must provide a list of dictionaries containing
        the parameters specified above; the same restrictions apply.
        For example:

            [{
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
              "mode": "audit",
              "is_active": "False",
              "enrollment_attributes": [
                {
                  "namespace": "credit",
                  "name": "provider_id",
                  "value": "institution_name"
                }
              ]
             },
             {
              "email": "janedoe@example.com",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
              "mode": "audit",
              "is_active": "True",
              "enrollment_attributes": []
             },
            ]

        **Returns**

        - 200: Success, enrollment created.
        - 202: User doesn't belong to site.
        - 400: Bad request, invalid course_id or missing either email or username.
        """
        data = request.data
        return EdxappEnrollment.prepare_multiresponse(
            data, self.single_enrollment_create
        )

    @apidocs.schema(
        body=EdxappCourseEnrollmentSerializer,
        responses={
            200: EdxappCourseEnrollmentSerializer,
            202: "User or enrollment doesn't belong to site.",
            400: "Bad request, invalid course_id or missing either email or username.",
        },
    )
    @audit_drf_api(action='Update enrollments on edxapp', method_name='eox_core_api_method')
    def put(self, request, *args, **kwargs):
        """
        Update enrollments on edxapp

        **Example Requests**

            PUT /eox-core/api/v1/enrollment/

            Request data: {
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
              "mode": "audit",
              "is_active": "False",
              "enrollment_attributes": [
                {
                  "namespace": "credit",
                  "name": "provider_id",
                  "value": "institution_name"
                }
              ]
            }

        **Parameters**

        - `username` (**required**, string, _body_):
            The username used to identify a user enrolled on the course. Use either username or email.

        - `email` (**required**, string, _body_):
            The email used to identify a user enrolled on the course. Use either username or email.

        - `course_id` (**required**, string, _body_):
            The course id for the enrollment you want to update.

        - `mode` (**required**, string, _body_):
            The course mode for the enrollment. Must be available for the course.

        - `is_active` (boolean, _body_):
            Flag indicating whether the enrollment is active.

        - `enrollment_attributes` (list, _body_):
            An enrollment attribute can be used to add extra parameters for a specific course mode.
            It must be a dictionary containing the following:
            - namespace: namespace of the attribute
            - name: name of the attribute
            - value: value of the attribute

        **Returns**

        - 200: Success, enrollment updated.
        - 202: User or enrollment doesn't belong to site.
        - 400: Bad request, invalid course_id or missing either email or username.
        """
        data = request.data
        return EdxappEnrollment.prepare_multiresponse(
            data, self.single_enrollment_update
        )

    @apidocs.schema(
        parameters=[
            apidocs.query_parameter(
                name="username",
                param_type=str,
                description="**required**, The username used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="email",
                param_type=str,
                description="**required**, The email used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="course_id",
                param_type=str,
                description="**required**, The course id for the enrollment you want to check.",
            ),
        ],
        responses={
            200: EdxappCourseEnrollmentSerializer,
            400: "Bad request, missing course_id or either email or username",
            404: "User or course not found",
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieves enrollment information given a user and a course_id

        **Example Requests**

            GET /eox-core/api/v1/enrollment/?username=johndoe&
            course_id=course-v1:edX+DemoX+Demo_Course

            Request data: {
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
            }

        **Returns**

        - 200: Success, enrollment found.
        - 400: Bad request, missing course_id or either email or username
        - 404: User or course not found
        """
        user_query = self.get_user_query(request)
        user = get_edxapp_user(**user_query)

        course_id = self.query_params.get("course_id", None)

        if not course_id:
            raise ValidationError(detail="You have to provide a course_id")

        enrollment_query = {
            "username": user.username,
            "course_id": course_id,
        }
        enrollment, errors = get_enrollment(**enrollment_query)

        if errors:
            raise NotFound(detail=errors)
        response = EdxappCourseEnrollmentSerializer(enrollment).data
        return Response(response)

    @apidocs.schema(
        parameters=[
            apidocs.query_parameter(
                name="username",
                param_type=str,
                description="**required**, The username used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="email",
                param_type=str,
                description="**required**, The email used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="course_id",
                param_type=str,
                description="**required**, The course id for the enrollment you want to check.",
            ),
        ],
        responses={
            204: "Empty response",
            400: "Bad request, missing course_id or either email or username",
            404: "User or course not found",
        },
    )
    @audit_drf_api(action='Delete enrollment on edxapp.', method_name='eox_core_api_method')
    def delete(self, request, *args, **kwargs):
        """
        Delete enrollment on edxapp

        **Example Requests**

            DELETE /eox-core/api/v1/enrollment/

            Request data: {
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
            }
        """
        user_query = self.get_user_query(request)
        user = get_edxapp_user(**user_query)

        course_id = self.query_params.get("course_id", None)

        if not course_id:
            raise ValidationError(detail="You have to provide a course_id")

        delete_enrollment(user=user, course_id=course_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    def single_enrollment_update(self, *args, **kwargs):
        """
        Handle one update at the time
        """
        user_query = self.get_user_query(None, query_params=kwargs)
        user = get_edxapp_user(**user_query)

        course_id = kwargs.pop("course_id", None)
        if not course_id:
            raise ValidationError(detail="You have to provide a course_id for updates")
        mode = kwargs.pop("mode", None)

        return update_enrollment(user, course_id, mode, **kwargs)

    @staticmethod
    def prepare_multiresponse(request_data, action_method):
        """
        Prepare a multiple part response according to the request_data and the action_method provided
        Args:
            request_data: Data dictionary containing the query or queries to be processed
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

        if many or "bundle_id" in request_data:
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
            LOG.error("API Error: %s", repr(exc.detail))

        return super(EdxappEnrollment, self).handle_exception(exc)


class EdxappPreEnrollment(APIView):
    """
    Handles API requests to manage whitelistings (pre-enrollments)
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @audit_drf_api(action='Create pre-enrollments on edxapp.', method_name='eox_core_api_method')
    def post(self, request, *args, **kwargs):
        """
        Create whitelistings on edxapp
        """
        serializer = EdxappCoursePreEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course_id = data.pop("course_id", None)
        pre_enrollment, warning = create_pre_enrollment(course_id=course_id, **data)
        response_data = EdxappCoursePreEnrollmentSerializer(
            pre_enrollment, context=warning
        ).data
        return Response(response_data)

    @audit_drf_api(action='Update pre-enrollments on edxapp.', method_name='eox_core_api_method')
    def put(self, request, *args, **kwargs):
        """
        Update whitelistings on edxapp
        """
        serializer = EdxappCoursePreEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data.get("email")
        course_id = data.get("course_id")
        auto_enroll = data.pop("auto_enroll", False)

        pre_enrollment_query = {
            "email": email,
            "course_id": course_id,
        }

        pre_enrollment = get_pre_enrollment(**pre_enrollment_query)
        update_query = {
            "pre_enrollment": pre_enrollment,
            "auto_enroll": auto_enroll,
        }
        updated_pre_enrollment = update_pre_enrollment(**update_query)
        response = EdxappCoursePreEnrollmentSerializer(updated_pre_enrollment).data
        return Response(response)

    @audit_drf_api(action='Delete pre-enrollments on edxapp.', method_name='eox_core_api_method')
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
        email = data.get("email")
        course_id = data.get("course_id")

        pre_enrollment_query = {
            "email": email,
            "course_id": course_id,
        }

        pre_enrollment = get_pre_enrollment(**pre_enrollment_query)
        delete_query = {
            "pre_enrollment": pre_enrollment,
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
        self.log("API Error", data, exc)
        return super(EdxappPreEnrollment, self).handle_exception(exc)

    def log(self, desc, data, exception=None):
        """
        log util for this view
        """
        log_data = []
        log_data.append(desc)
        log_data.append("Exception:")
        if isinstance(exception, APIException):
            log_data.append(repr(exception.detail))
        else:
            log_data.append(repr(exception))

        log_data.append("Request data:")
        if not data:
            log_data.append("Empty request")
        else:
            for key, value in data.items():
                log_data.append("{}: {}".format(key, value))

        LOG.error(" ".join(log_data))


class EdxappGrade(UserQueryMixin, APIView):
    """
    Handles API requests to manage course grades
    """

    authentication_classes = (BearerAuthentication, SessionAuthentication)
    permission_classes = (EoxCoreAPIPermission,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    @apidocs.schema(
        parameters=[
            apidocs.query_parameter(
                name="username",
                param_type=str,
                description="**required**, The username used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="email",
                param_type=str,
                description="**required**, The email used to identify a user enrolled on the course. Use either username or email.",
            ),
            apidocs.query_parameter(
                name="course_id",
                param_type=str,
                description="**required**, The course id for the enrollment you want to check.",
            ),
            apidocs.query_parameter(
                name="detailed",
                param_type=bool,
                description="**optional**, If true include detailed data for each graded subsection",
            ),
            apidocs.query_parameter(
                name="grading_policy",
                param_type=bool,
                description="**optional**, If true include course grading policy.",
            ),
        ],
        responses={
            200: EdxappGradeSerializer,
            400: "Bad request, missing course_id or either email or username",
            404: "User, course or enrollment not found",
        },
    )
    def get(self, request):
        """
        Retrieves Grades information for given a user and course_id

        **Example Requests**

            GET /eox-core/api/v1/grade/?username=johndoe&course_id=course-v1:edX+DemoX+Demo_Course

            Request data: {
              "username": "johndoe",
              "course_id": "course-v1:edX+DemoX+Demo_Course",
            }

        **Response details**

        - `earned_grade`: Final user score for the course.
        - `section_breakdown` (**optional**): Details of each grade subsection.
            - `attempted`: Whether the learner attempted the assignment.
            - `assignment_type`: General category of the assignment.
            - `percent`: Grade obtained by the user on this subsection.
            - `score_earned`: The score a user earned on this subsection.
            - `score_possible`: Highest possible score a user can earn on this subsection.
            - `subsection_name`: Name of the subsection.
        - `grading_policy` (**optional**): Course grading policy.
            - `grade_cutoff`: Score needed to reach each grade.
            - `grader`: Details of each assignment type used by the Grader.
                - `assignment_type`: General category of the assignment.
                - `count`: Number of assignments of this type.
                - `dropped`: The number of assignments of this type that the grader will drop. The grader will drop the lowest-scored assignments first.
                - `weight`: Weight of this type of assignment towards the final grade.

        More information about grading can be found in the
        [edX documentation](https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/student_progress/course_grades.html).

        **Returns**

        - 200: Success.
        - 400: Bad request, missing course_id or either email or username.
        - 404: User, course or enrollment not found.
        """
        user_query = self.get_user_query(request)
        user = get_edxapp_user(**user_query)

        course_id = self.query_params.get("course_id", None)
        detailed = self.query_params.get("detailed", False)
        grading_policy = self.query_params.get("grading_policy", False)

        if not course_id:
            raise ValidationError(detail="You have to provide a course_id")

        _, errors = get_enrollment(username=user.username, course_id=course_id)

        if errors:
            raise NotFound(errors)

        grade_factory = get_course_grade_factory()
        course_key = get_valid_course_key(course_id)
        course = get_courseware_courses().get_course_by_id(course_key)
        course_grade = grade_factory().read(user, course)
        response = {"earned_grade": course_grade.percent}

        if detailed in ("True", "true", "on", "1"):
            breakdown = self._section_breakdown(course_grade.subsection_grades)
            response["section_breakdown"] = breakdown
        if grading_policy in ("True", "true", "on", "1"):
            response["grading_policy"] = course.grading_policy

        return Response(EdxappGradeSerializer(response).data)

    def _section_breakdown(self, subsection_grades):
        """
        Given a list of subsections grades determine if the subsection is
        graded and creates a list of grade data for each subsection.

        This logic comes from `edunext-platform/lms/djangoapps/grades/rest_api/v1/gradebook_views`
        with a few changes in the return value: `label` and `module_id` were
        removed and `category` was renamed to `assignment_type` to keep
        consistency with the names used in `grading_policy`.
        """
        breakdown = []
        for subsection in subsection_grades.values():
            if not subsection.graded:
                continue

            attempted = False
            score_earned = 0
            score_possible = 0

            if subsection.attempted_graded or subsection.override:
                attempted = True
                score_earned = subsection.graded_total.earned
                score_possible = subsection.graded_total.possible

            breakdown.append(
                {
                    "attempted": attempted,
                    "assignment_type": subsection.format,
                    "percent": subsection.percent_graded,
                    "score_earned": score_earned,
                    "score_possible": score_possible,
                    "subsection_name": subsection.display_name,
                }
            )
        return breakdown


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
            "user": six.text_type(request.user.username),
            "email": six.text_type(request.user.email),
            "auth": six.text_type(request.auth),
        }

        if request.user.is_staff:
            content["is_superuser"] = request.user.is_superuser
            content["is_staff"] = request.user.is_staff

        return Response(content)
