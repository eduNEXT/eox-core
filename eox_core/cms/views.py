# -*- coding: utf-8 -*-
"""
API endpoints for Course Management view.
"""
from __future__ import unicode_literals

import json
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error
from rest_framework import status

from eox_core.edxapp_wrapper.courses import (
    get_course_details_fields,
    get_courses_accessible_to_user,
    get_first_course_key,
    get_process_courses_list,
)
from eox_core.edxapp_wrapper.edxmako_module import render_to_response
from eox_core.edxapp_wrapper.users import get_course_team_user

from .helpers import enable_course_management_view


@enable_course_management_view
@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def management_view(request):
    """
    Renders the course management view.
    """
    if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
        details_fields = get_course_details_fields()
        course_key = get_first_course_key()
        request_timeout_value = getattr(settings, 'EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT', 500)

        return render_to_response(u'management.html', {
            'course_key': course_key,
            'details_fields': details_fields,
            'request_timeout_value': request_timeout_value
        })
    return HttpResponseNotFound()


@enable_course_management_view
@login_required
@ensure_csrf_cookie
@require_http_methods(["POST", "DELETE"])
def course_team(request, *args, **kwargs):  # pylint: disable=too-many-locals
    """
    **Use Cases**
        Add or change the course team status role.

    **Example Requests**:
        POST, DELETE <studio-url>/eox-core/management/course-team-management

    **Request Values**

        * org: Organization short name.
        * user: user email.
        * role: user role (staff, instructor, '')

        Note: If the role value is empty, then it must be sent as a DELETE operation.

    **Response Values**

        * message: Status message of the operation.
        * status: Global operaion status.
            Failed, Success, No complete.
        * failed_tasks: Array containing the course failed tasks.
            message: Failed message reason.
            course: Plain course key.
        * complete_tasks: Array containing the course failed tasks.
            message: 'success'
            course: Plain course key.
    """

    json_content = get_json_from_body_request(request)
    if not json_content:
        data = {
            'message': 'Invalid request JSON',
            'status': 'Failed'
        }
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

    org = json_content.get('org', '')
    user_email = json_content.get('user')
    courses_iter, in_process_course_actions = get_courses_accessible_to_user(request, org)
    active_courses, archived_courses = get_process_courses_list(courses_iter, in_process_course_actions)  # pylint: disable=unused-variable

    if not org:  # pylint: disable=no-else-return
        data = {
            'message': 'Incorrect organization name.',
            'status': 'Failed'
        }
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
    elif not active_courses:
        data = {
            'message':
                'The organization {} does not exists, or does not have active courses.'.format(org),
            'status': 'Failed'
        }
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

    data = {
        'failed_tasks': [],
        'complete_tasks': [],
        'message': 'Operation complete.',
        'status': 'Success'
    }

    # Loop over each organization course.
    for course in active_courses:
        plain_course_key = course.get('course_key')
        course_key = CourseKey.from_string(plain_course_key)
        course_team_response = get_course_team_user(request, course_key, user_email)
        per_course_data = {}

        if course_team_response.status_code != 204:
            error_messages = json.loads(course_team_response.content)
            per_course_data = {
                'message': error_messages.get('error'),
                'course': plain_course_key
            }
            data.get('failed_tasks').append(per_course_data)
        else:
            per_course_data = {
                'message': 'success',
                'course': plain_course_key
            }
            data.get('complete_tasks').append(per_course_data)

    if data['failed_tasks']:
        data['message'] = 'Some issues were found.'
        data['status'] = 'No complete'
    return JsonResponse(data)


@enable_course_management_view
@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_courses_by_course_regex(request, *args, **kwargs):
    """
    **Use Cases**
        Get a list of course keys that match with the provided query string.
        E.g:
            course-v1:FP+DAT248x+2018*
            course-v1:FP+DAT*
            course-v1:FP*
            *DAT248x+2018*


    **Example Requests**:
        GET <studio-url>/eox-core/management/get_courses?search=<query-string>

    **Request Values**

        * search: Query string of the desired course matching.

    **Response Values**

        * message: Status message of the operation.
        * status: Global operaion status.
            Failed, Success.
        * courses: List containing the course/s key/s that match with the provided query string.
    """

    input_course_regex = request.GET.get('search')
    if not input_course_regex:
        data = {
            'message': 'No course regex provided.',
            'status': 'Failed'
        }
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

    match_courses = []
    course_regex = get_course_regex(input_course_regex)

    courses_iter, in_process_course_actions = get_courses_accessible_to_user(request)
    active_courses, archived_courses = get_process_courses_list(courses_iter, in_process_course_actions)  # pylint: disable=unused-variable

    if not active_courses:
        data = {
            'message': 'No courses were found.',
            'status': 'Failed',
            'courses': []
        }
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

    for course in active_courses:
        plain_course_key = course.get('course_key')
        match = course_regex.search(plain_course_key)
        if match:
            match_courses.append(plain_course_key)

    if not match_courses:
        data = {
            'message': 'No courses match with this: "{}" query string.'.format(
                input_course_regex
            ),
            'status': 'Failed',
            'courses': []
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

    data = {
        'message': '{} course/s were found.'.format(
            len(match_courses)
        ),
        'status': 'Success',
        'courses': match_courses
    }

    return JsonResponse(data, status=status.HTTP_200_OK)


def get_json_from_body_request(request):
    """
    Function to convert request.body into a json format.
    """
    json_content = {}
    if 'application/json' in request.META.get('CONTENT_TYPE', '') and request.body:
        try:
            json_content = json.loads(request.body)
        except ValueError:
            return json_content
    return json_content


def get_course_regex(input_course_regex):
    """
    Returns the final course regex to match with the courses keys.

    Since the input string could be a course key like value (course-v1:FP+DAT*),
    we need to replace '+' and wildcard '*' characters to '.*' character in order to build
    a correct regular expression string.
    """
    search_value_replaced = input_course_regex.replace('*', '.*')
    splitted_search_value = search_value_replaced.split('+')
    final_regex_string = '.*'.join(splitted_search_value)
    course_regex = re.compile(r"{}".format(final_regex_string))

    return course_regex
