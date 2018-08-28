#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""

from __future__ import absolute_import, unicode_literals
from enrollment import api
from enrollment.errors import CourseModeNotFoundError
from enrollment.errors import (
    CourseEnrollmentClosedError,
    CourseEnrollmentExistsError,
    CourseEnrollmentFullError,
    InvalidEnrollmentAttribute,
    UserNotFoundError
)
from openedx.core.lib.exceptions import CourseNotFoundError
from course_modes.models import CourseMode
from rest_framework.exceptions import APIException
from opaque_keys.edx.keys import CourseKey
from django.contrib.auth.models import User
from six import text_type
from student.models import (
    AlreadyEnrolledError,
    CourseEnrollment,
    CourseFullError,
    EnrollmentClosedError,
    NonExistentCourseError
)
import logging

log = logging.getLogger(__name__)


def create_enrollment(*args, **kwargs):

    errors = []
    email = kwargs.get("email")
    username = kwargs.get('username')
    course_id = kwargs.get('course_id')
    mode = kwargs.get('mode')
    is_active = kwargs.get('is_active', True)
    force_registration = kwargs.get('force_registration', False)
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

        if force_registration:
            # code copied from edx-platform/common/djangoapps/enrollment/data.py@create_course_enrollment
            # the only change is check_access=True to check_access=False and remove "return" keyword
            # (Open edx version=0.10)
            course_key = CourseKey.from_string(course_id)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                msg = u"Not user with username '{username}' found.".format(username=username)
                log.warn(msg)
                raise UserNotFoundError(msg)
            try:
                enrollment = CourseEnrollment.enroll(user, course_key, check_access=False)
                api._data_api()._update_enrollment(enrollment, is_active=is_active, mode=mode)
            except NonExistentCourseError as err:
                raise CourseNotFoundError(text_type(err))
            except EnrollmentClosedError as err:
                raise CourseEnrollmentClosedError(text_type(err))
            except CourseFullError as err:
                raise CourseEnrollmentFullError(text_type(err))
            except AlreadyEnrolledError as err:
                enrollment = api._data_api().get_course_enrollment(username, course_id)
                raise CourseEnrollmentExistsError(text_type(err), enrollment)
            # code copy ends
        else:
            # if force registration is false we just call the open edx-platform function create_course_enrollment
            enrollment = api._data_api().create_course_enrollment(username, course_id, mode, is_active)

        if enrollment_attributes is not None:
            api.set_enrollment_attributes(username, course_id, enrollment_attributes)
    except CourseEnrollmentExistsError as e:
        if force_registration:
            enrollment = api._data_api().update_course_enrollment(username, course_id, mode, is_active)
        else:
            raise APIException(repr(e) + ", use force_registration to update the existing enrollment")
    except (UserNotFoundError, InvalidEnrollmentAttribute, CourseNotFoundError, CourseEnrollmentFullError, CourseEnrollmentClosedError) as e:
        raise APIException(repr(e))

    return enrollment, errors


def check_edxapp_enrollment_is_valid(*args, **kwargs):
    errors = []
    is_active = kwargs.get("is_active", True)
    course_id = kwargs.get("course_id")
    force_registration = kwargs.get('force_registration', False)
    mode = kwargs.get("mode")
    if not kwargs.get("email") and not kwargs.get("username"):
        return ['Email or username needed']
    if kwargs.get("email") and kwargs.get("username"):
        return ['You have to provide an email or username but not both']
    if mode not in CourseMode.ALL_MODES:
        return ['Invalid mode given:' + mode]
    if not force_registration:
        try:
            api.validate_course_mode(course_id, mode, is_active=is_active)
        except CourseModeNotFoundError:
            errors.append('Mode not found')
    return errors
