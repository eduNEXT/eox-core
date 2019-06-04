#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
# pylint: disable=import-error, protected-access
from __future__ import absolute_import, unicode_literals

import datetime
import logging

from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from pytz import utc
from rest_framework.exceptions import APIException

from course_modes.models import CourseMode
from enrollment import api
from enrollment.errors import (CourseEnrollmentExistsError,
                               CourseModeNotFoundError)
from eox_core.edxapp_wrapper.backends.edxfuture_i_v1 import get_program
from eox_core.edxapp_wrapper.users import check_edxapp_account_conflicts
from openedx.core.djangoapps.content.course_overviews.models import \
    CourseOverview
from openedx.core.djangoapps.site_configuration.helpers import (get_all_orgs,
                                                                get_current_site_orgs)
from openedx.core.lib.exceptions import CourseNotFoundError
from student.models import CourseEnrollment

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

def update_enrollment(*args, **kwargs):
    """
    Update enrollment of given user in the course provided.

    Example:
        >>>update_enrollment(
            {
            "username": "Bob",
            "course_id": course-v1-edX-DemoX-1T2015",
            "is_active": "False",
            "mode": "audit",
            "enrollment_attributes": [
                {
                    "namespace": "credit",
                    "name": "provider_id",
                    "value": "hogwarts",
                },
                {...}
                ]
            }
        )
    """
    errors = []
    course_id = kwargs.pop('course_id', None)
    email = kwargs.get("email")
    username = kwargs.get('username')
    mode = kwargs.get('mode')
    is_active = kwargs.get('is_active', True)
    enrollment_attributes = kwargs.get('enrollment_attributes', None)

    if email:
        match = User.objects.filter(email=email).first()
        if match is None:
            raise APIException('No user found with that email')
        else:
            username = match.username
            email = match.email
    LOG.info('Updating enrollment for student: %s of course: %s mode: %s', username, course_id, mode)
    enrollment = api._data_api().update_course_enrollment(username, course_id, mode, is_active)
    if not enrollment:
        raise APIException('No enrollment found for {}'.format(username or email))
    if enrollment_attributes is not None:
        api.set_enrollment_attributes(username, course_id, enrollment_attributes)

    enrollment['enrollment_attributes'] = enrollment_attributes
    enrollment['course_id'] = course_id
    return enrollment, errors


def get_enrollment(*args, **kwargs):
    """
    Return enrollment of given user in the course provided.

    Example:
        >>>get_enrollment(
            {
            "username": "Bob",
            "course_id": "course-v1-edX-DemoX-1T2015"
            }
        )
    """
    errors = []
    course_id = kwargs.pop('course_id', None)
    username = kwargs.get('username', None)
    email = kwargs.get('email', None)
    try:
        if username:
            user = User.objects.get(username=username)
        else:
            user = User.objects.get(email=email)
    except User.DoesNotExist: # pylint: disable=no-member
        errors.append('No user found by {query} .'.format(query=str(kwargs)))
        return None, errors

    username = user.username
    email = user.email

    try:
        LOG.info('Getting enrollment information of student: %s  course: %s', username, course_id)
        enrollment = api.get_enrollment(username, course_id)
        if not enrollment:
            errors.append('No enrollment found for {}'.format(username))
            return None, errors
    except InvalidKeyError:
        errors.append('No course found for course_id {}'.format(course_id))
        return None, errors
    enrollment['enrollment_attributes'] = api.get_enrollment_attributes(username, course_id)
    enrollment['course_id'] = course_id
    return enrollment, errors

def delete_enrollment(*args, **kwargs):
    """
    Delete enrollment and enrollment attributes of given user in the course provided.

    Example:
        >>>delete_enrollment(
            {
            "username": "Bob",
            "course_id": course-v1-edX-DemoX-1T2015"
        )
    """
    course_id = kwargs.pop('course_id', None)
    course_key = CourseKey.from_string(course_id)
    username = kwargs.get('username', None)
    email = kwargs.get('email', None)
    try:
        if username:
            user = User.objects.get(username=username)
        else:
            user = User.objects.get(email=email)
    except User.DoesNotExist: # pylint: disable=no-member
        raise APIException('No user found by {query} .'.format(query=str(kwargs)))

    username = user.username

    LOG.info('Deleting enrollment student: %s  course: %s', username, course_id)
    enrollment = CourseEnrollment.get_enrollment(user, course_key)
    if not enrollment:
        raise APIException('No enrollment found for {}'.format(username))
    try:
        enrollment.delete()
    except Exception:
        raise APIException('Error: Enrollment could not be deleted for {}'.format(username))


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
            email = match.email

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

    enrollment['enrollment_attributes'] = enrollment_attributes
    enrollment['course_id'] = course_id
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
    username = kwargs.get("username")
    email = kwargs.get("email")

    if program_uuid and course_id:
        return None, ['You have to provide a course_id or bundle_id but not both']
    if not email and not username:
        return ['Email or username needed']
    if not check_edxapp_account_conflicts(email=email, username=username):
        return ['User not found']
    if mode not in CourseMode.ALL_MODES:
        return ['Invalid mode given:' + mode]
    if course_id:
        if not _validate_org(course_id):
            errors.append('Enrollment not allowed for given org')
    if course_id and not force:
        try:
            api.validate_course_mode(course_id, mode, is_active=is_active)
        except CourseModeNotFoundError:
            errors.append('Mode not found')
        except CourseNotFoundError:
            errors.append('Course not found')
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


def _validate_org(course_id):
    """
    Validates the course organization against all possible orgs for the site
    """
    course_key = CourseKey.from_string(course_id)
    current_site_orgs = get_current_site_orgs() or []

    if not current_site_orgs:
        if course_key.org in get_all_orgs():
            return False
        return True
    else:
        return course_key.org in current_site_orgs
