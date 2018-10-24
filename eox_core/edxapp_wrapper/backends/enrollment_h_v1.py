#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
# pylint: disable=import-error, protected-access
from __future__ import absolute_import, unicode_literals
import logging
import datetime
from pytz import utc
from rest_framework.exceptions import APIException
from django.contrib.auth.models import User
from enrollment import api
from enrollment.errors import CourseModeNotFoundError
from enrollment.errors import CourseEnrollmentExistsError
from course_modes.models import CourseMode
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment
from eox_core.edxapp_wrapper.backends.edxfuture_i_v1 import get_program
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.lib.exceptions import CourseNotFoundError

LOG = logging.getLogger(__name__)


def create_enrollment(*args, **kwargs):
    """
    backend function to create enrollment
    """
    kwargs = dict(kwargs)
    program_uuid = kwargs.pop('bundle_id', None)
    course_id = kwargs.pop('course_id', None)

    if program_uuid:
        return enroll_on_program(program_uuid, *args, **kwargs)

    return enroll_on_course(course_id, *args, **kwargs)


def enroll_on_course(course_id, *args, **kwargs):
    """
    enroll user on a single course
    """
    errors = []
    email = kwargs.get("email")
    username = kwargs.get('username')
    mode = kwargs.get('mode')
    is_active = kwargs.get('is_active', True)
    force = kwargs.get('force', False)
    enrollment_attributes = kwargs.get('enrollment_attributes', None)
    validation_errors = check_edxapp_enrollment_is_valid(*args, **kwargs)
    if validation_errors:
        return None, [", ".join(validation_errors)]
    if email:
        match = User.objects.filter(email=email).first()
        if match is None:
            raise APIException('No user found with that email')
        else:
            username = match.username

    try:
        LOG.info('Creating regular enrollment %s, %s, %s', username, course_id, mode)
        enrollment = _create_or_update_enrollment(username, course_id, mode, is_active, force)
    except CourseNotFoundError as err:
        raise APIException(repr(err))
    except Exception as err:  # pylint: disable=broad-except
        if force:
            LOG.info('Force create enrollment %s, %s, %s', username, course_id, mode)
            enrollment = _force_create_enrollment(username, course_id, mode, is_active)
        else:
            raise APIException(repr(err))

    if enrollment_attributes is not None:
        api.set_enrollment_attributes(username, course_id, enrollment_attributes)

    return enrollment, errors


def enroll_on_program(program_uuid, *arg, **kwargs):
    """
    enroll user on each of the courses of a progam
    """
    results = []
    errors = []
    LOG.info('Enrolling on program: %s', program_uuid)
    try:
        data = get_program(program_uuid)
    except Exception as err:  # pylint: disable=broad-except
        raise APIException(repr(err))
    if not data['courses']:
        raise APIException("No courses found for this program")
    for course in data['courses']:
        if course['course_runs']:
            course_run = get_preferred_course_run(course)
            LOG.info('Enrolling on course_run: %s', course_run['key'])
            course_id = course_run['key']
            result, errors_list = enroll_on_course(course_id, *arg, **kwargs)
            results.append(result)
            errors.append(errors_list)
        else:
            raise APIException("No course runs available for this course")
    return results, errors


def get_preferred_course_run(course):
    """
    Returns the course run more likely to be the intended one
    """
    sorted_course_runs = sorted(course['course_runs'], key=lambda run: run['start'])

    for run in sorted_course_runs:
        default_enrollment_start_date = datetime.datetime(1900, 1, 1, tzinfo=utc)
        course_run_key = CourseKey.from_string(run['key'])
        course_overview = CourseOverview.get_from_id(course_run_key)
        enrollment_end = course_overview.enrollment_end or datetime.datetime.max.replace(tzinfo=utc)
        enrollment_start = course_overview.enrollment_start or default_enrollment_start_date
        run['is_enrollment_open'] = enrollment_start <= datetime.datetime.now(utc) < enrollment_end

    open_course_runs = [run for run in sorted_course_runs if run['is_enrollment_open']]
    course_run = open_course_runs[0] if open_course_runs else sorted_course_runs[-1]
    return course_run


# pylint: disable=invalid-name
def check_edxapp_enrollment_is_valid(*args, **kwargs):
    """
    backend function to check if enrollment is valid
    """
    errors = []
    is_active = kwargs.get("is_active", True)
    course_id = kwargs.get("course_id")
    force = kwargs.get('force', False)
    mode = kwargs.get("mode")
    program_uuid = kwargs.get('bundle_id')

    if program_uuid and course_id:
        return None, ['You have to provide a course_id or bundle_id but not both']
    if not kwargs.get("email") and not kwargs.get("username"):
        return ['Email or username needed']
    if kwargs.get("email") and kwargs.get("username"):
        return ['You have to provide an email or username but not both']
    if mode not in CourseMode.ALL_MODES:
        return ['Invalid mode given:' + mode]
    if course_id and not force:
        try:
            api.validate_course_mode(course_id, mode, is_active=is_active)
        except CourseModeNotFoundError:
            errors.append('Mode not found')
    return errors


def _create_or_update_enrollment(username, course_id, mode, is_active, try_update):
    """
    non-forced create or update enrollment internal function
    """
    try:
        enrollment = api._data_api().create_course_enrollment(username, course_id, mode, is_active)
    except CourseEnrollmentExistsError as err:
        if try_update:
            enrollment = api._data_api().update_course_enrollment(username, course_id, mode, is_active)
        else:
            raise Exception(repr(err) + ", use force to update the existing enrollment")
    return enrollment


def _force_create_enrollment(username, course_id, mode, is_active):
    """
    forced create enrollment internal function
    """
    try:
        course_key = CourseKey.from_string(course_id)
        user = User.objects.get(username=username)
        enrollment = CourseEnrollment.enroll(user, course_key, check_access=False)
        api._data_api()._update_enrollment(enrollment, is_active=is_active, mode=mode)
    except Exception as err:  # pylint: disable=broad-except
        raise APIException(repr(err))
    return enrollment
