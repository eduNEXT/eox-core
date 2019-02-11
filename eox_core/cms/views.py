# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-error
from rest_framework import status
from rest_framework.response import Response

from eox_core.edxapp_wrapper.courses import (get_courses_accessible_to_user,
                                             get_process_courses_list,
                                             get_course_settings_fields,
                                             get_course_details_fields,)
from eox_core.edxapp_wrapper.edxmako_module import render_to_response
from eox_core.edxapp_wrapper.site_configuration import get_all_orgs_helper
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
    if 'text/html' in request.META.get('HTTP_ACCEPT', '') and request.method == 'GET':
        org_list = get_all_orgs()
        settings_fields = get_course_settings_fields()
        details_fields = get_course_details_fields()

        return render_to_response(u'management.html', {
            'list_org': org_list,
            'settings_fileds': settings_fields,
            'details_fields': details_fields,
        })


@enable_course_management_view
@login_required
@ensure_csrf_cookie
@require_http_methods(["POST", "DELETE"])
def course_team(request, *args, **kwargs):
    """
    **Use Cases**
        Add or change the course team status role.

    **Example Requests**:
        <studio-url>/eox-core/management/course-team-management

    **Request Values**

        * org: Organization short name.
        * user: user email.
        * role: user role (staff, instructor, '')

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
    active_courses, archived_courses = get_process_courses_list(courses_iter, in_process_course_actions)

    if not org:
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


def get_all_orgs():
    """
    Return organization list.
    """
    organizations_raw = get_all_orgs_helper()
    organization_list = list(organizations_raw)
    # Add a empty value to be used inside of select html tag.
    organization_list.insert(0, ' ')

    return organization_list


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
