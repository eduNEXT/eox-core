#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/lilac.master tag
"""
# pylint: disable=import-error, protected-access
import datetime
import logging

from common.djangoapps.course_modes.models import CourseMode
from common.djangoapps.student.models import CourseEnrollment
from django.contrib.auth.models import User
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.enrollments import api  # pylint: disable=ungrouped-imports
from openedx.core.djangoapps.enrollments.errors import (  # pylint: disable=ungrouped-imports
    CourseEnrollmentExistsError,
    CourseModeNotFoundError,
)
from openedx.core.lib.exceptions import CourseNotFoundError
from pytz import utc
from rest_framework.exceptions import APIException, NotFound

from eox_core.edxapp_wrapper.backends.edxfuture_i_v1 import get_program
from eox_core.edxapp_wrapper.coursekey import get_valid_course_key, validate_org
from eox_core.edxapp_wrapper.users import check_edxapp_account_conflicts

LOG = logging.getLogger(__name__)


def create_enrollment(user, *args, **kwargs):
    """
    backend function to create enrollment

    Example:
        >>>create_enrollment(
            user_object,
            {
            "course_id": "course-v1-edX-DemoX-1T2015",
            ...
            }
        )

    """
    kwargs = dict(kwargs)
    program_uuid = kwargs.pop('bundle_id', None)
    course_id = kwargs.pop('course_id', None)

    if program_uuid:
        return _enroll_on_program(user, program_uuid, *args, **kwargs)
    if course_id:
        return _enroll_on_course(user, course_id, *args, **kwargs)

    raise APIException("You have to provide a course_id or bundle_id")


def update_enrollment(user, course_id, mode, *args, **kwargs):
    """
    Update enrollment of given user in the course provided.

    Example:
        >>>update_enrollment(
            user_object,
            course_id,
            mode,
            is_active=False,
            enrollment_attributes=[
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
    username = user.username

    is_active = kwargs.get('is_active', True)
    enrollment_attributes = kwargs.get('enrollment_attributes', None)

    LOG.info('Updating enrollment for student: %s of course: %s mode: %s', username, course_id, mode)
    enrollment = api._data_api().update_course_enrollment(username, course_id, mode, is_active)
    if not enrollment:
        raise NotFound('No enrollment found for {}'.format(username))
    if enrollment_attributes is not None:
        api.set_enrollment_attributes(username, course_id, enrollment_attributes)

    return {
        'user': enrollment['user'],
        'course_id': course_id,
        'mode': enrollment['mode'],
        'is_active': enrollment['is_active'],
        'enrollment_attributes': enrollment_attributes,
    }


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

    try:
        LOG.info('Getting enrollment information of student: %s  course: %s', username, course_id)
        enrollment = api.get_enrollment(username, course_id)
        if not enrollment:
            errors.append('No enrollment found for user:`{}`'.format(username))
            return None, errors
    except InvalidKeyError:
        errors.append('No course found for course_id `{}`'.format(course_id))
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
            "user": user_object,
            "course_id": course-v1-edX-DemoX-1T2015"
        )
    """
    course_id = kwargs.pop('course_id', None)
    user = kwargs.get('user')
    try:
        course_key = get_valid_course_key(course_id)
    except InvalidKeyError:
        raise NotFound('No course found by course id `{}`'.format(course_id))

    username = user.username

    LOG.info('Deleting enrollment. User: `%s`  course: `%s`', username, course_id)
    enrollment = CourseEnrollment.get_enrollment(user, course_key)
    if not enrollment:
        raise NotFound('No enrollment found for user: `{}` on course_id `{}`'.format(username, course_id))
    try:
        enrollment.delete()
    except Exception:
        raise NotFound('Error: Enrollment could not be deleted for user: `{}` on course_id `{}`'.format(username, course_id))


def _enroll_on_course(user, course_id, *args, **kwargs):
    """
    enroll user on a single course

    Example:
        >>>_enroll_on_course(
            {
            "user": user_object,
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

    username = user.username

    mode = kwargs.get('mode', 'audit')
    is_active = kwargs.get('is_active', True)
    force = kwargs.get('force', False)
    enrollment_attributes = kwargs.get('enrollment_attributes', None)

    enrollment_valid_query = {
        'course_id': course_id,
        'force': force,
        'mode': mode,
        'username': username,
    }
    validation_errors = check_edxapp_enrollment_is_valid(**enrollment_valid_query)
    if validation_errors:
        return None, [", ".join(validation_errors)]

    try:
        LOG.info('Creating regular enrollment %s, %s, %s', username, course_id, mode)
        enrollment = _create_or_update_enrollment(username, course_id, mode, is_active, force)
    except CourseNotFoundError as err:
        raise NotFound(repr(err))
    except Exception as err:  # pylint: disable=broad-except
        if force:
            LOG.info('Force create enrollment %s, %s, %s', username, course_id, mode)
            enrollment = _force_create_enrollment(username, course_id, mode, is_active)
        else:
            if not str(err):
                err = err.__class__.__name__
            raise APIException(detail=err)

    if enrollment_attributes is not None:
        api.set_enrollment_attributes(username, course_id, enrollment_attributes)
    try:
        enrollment['enrollment_attributes'] = enrollment_attributes
        enrollment['course_id'] = course_id
    except TypeError:
        pass
    return enrollment, errors


def _enroll_on_program(user, program_uuid, *arg, **kwargs):
    """
    enroll user on each of the courses of a program
    """
    results = []
    errors = []
    LOG.info('Enrolling on program: %s', program_uuid)
    try:
        data = get_program(program_uuid)
    except Exception as err:  # pylint: disable=broad-except
        raise NotFound(repr(err))
    if not data['courses']:
        raise NotFound("No courses found for this program")
    for course in data['courses']:
        if course['course_runs']:
            course_run = _get_preferred_course_run(course)
            LOG.info('Enrolling on course_run: %s', course_run['key'])
            course_id = course_run['key']
            try:
                result, errors_list = _enroll_on_course(user, course_id, *arg, **kwargs)
            except APIException as error:
                result = {
                    'username': user.username,
                    'mode': None,
                    'course_id': course_id,
                }
                errors_list = [error.detail]

            results.append(result)
            errors.append(errors_list)
        else:
            raise NotFound("No course runs available for this course")
    return results, errors


def _get_preferred_course_run(course):
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
        return ['You have to provide a course_id or bundle_id but not both']
    if not program_uuid and not course_id:
        return ['You have to provide a course_id or bundle_id']
    if not email and not username:
        return ['Email or username needed']
    if not check_edxapp_account_conflicts(email=email, username=username):
        return ['User not found']
    if mode not in CourseMode.ALL_MODES:
        return ['Invalid mode given:' + mode]
    if course_id:
        if not validate_org(course_id):
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
        course_key = get_valid_course_key(course_id)
        user = User.objects.get(username=username)
        enrollment = CourseEnrollment.enroll(user, course_key, check_access=False)
        api._data_api()._update_enrollment(enrollment, is_active=is_active, mode=mode)
    except Exception as err:  # pylint: disable=broad-except
        raise APIException(repr(err))
    return enrollment
