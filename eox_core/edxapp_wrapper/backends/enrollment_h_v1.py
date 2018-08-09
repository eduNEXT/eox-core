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


def create_enrollment(*args, **kwargs):

    errors = []
    user_id = kwargs.get('username')
    course_id = kwargs.get('course_id')
    mode = kwargs.get('mode')
    is_active = kwargs.get('is_active', True)
    enrollment_attributes = kwargs.get('enrollment_attributes', None)
    validation_errors = check_edxapp_enrollment_is_valid(*args, **kwargs)
    if validation_errors:
        return None, [", ".join(validation_errors)]
    try:
        enrollment = api._data_api().create_course_enrollment(user_id, course_id, mode, is_active)
        if enrollment_attributes is not None:
            api.set_enrollment_attributes(user_id, course_id, enrollment_attributes)
    except (UserNotFoundError, InvalidEnrollmentAttribute, CourseNotFoundError, CourseEnrollmentFullError, CourseEnrollmentClosedError, CourseEnrollmentExistsError) as e:
        enrollment = None
        raise APIException(repr(e))
    return enrollment, errors


def check_edxapp_enrollment_is_valid(*args, **kwargs):
    errors = []
    is_active = kwargs.get("is_active", True)
    course_id = kwargs.get("course_id")
    force_registration = kwargs.get('force_registration', False)
    mode = kwargs.get("mode")
    if mode not in CourseMode.ALL_MODES:
        return ['invalid mode given:' + mode]
    if not force_registration:
        try:
            api.validate_course_mode(course_id, mode, is_active=is_active)
        except CourseModeNotFoundError:
            errors.append('mode not found')
    return errors
