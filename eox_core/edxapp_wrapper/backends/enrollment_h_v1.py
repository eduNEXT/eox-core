#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the create_edxapp_user that works under the open-release/hawthorn.beta1 tag
"""
# pylint: disable=import-error, protected-access
from __future__ import absolute_import, unicode_literals
import logging
from django.contrib.auth.models import User
from enrollment import api
from enrollment.errors import CourseModeNotFoundError
from enrollment.errors import CourseEnrollmentExistsError
from course_modes.models import CourseMode
from rest_framework.exceptions import APIException
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment

LOG = logging.getLogger(__name__)


def create_enrollment(*args, **kwargs):
    """
    backend function to create enrollment
    """
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
        enrollment = _create_or_update_enrollment(username, course_id, mode, is_active, force_registration)
    except Exception as err:  # pylint: disable=broad-except
        if force_registration:
            enrollment = _force_create_enrollment(username, course_id, mode, is_active)
        else:
            raise APIException(repr(err))

    if enrollment_attributes is not None:
        api.set_enrollment_attributes(username, course_id, enrollment_attributes)

    return enrollment, errors


# pylint: disable=invalid-name
def check_edxapp_enrollment_is_valid(*args, **kwargs):
    """
    backend function to check if enrollment is valid
    """
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
            raise Exception(repr(err) + ", use force_registration to update the existing enrollment")
    return enrollment


def _force_create_enrollment(username, course_id, mode, is_active):
    """
    forced create enrollment internal function
    """
    LOG.info('Calling _force_create_enrollment')
    try:
        course_key = CourseKey.from_string(course_id)
        user = User.objects.get(username=username)
        enrollment = CourseEnrollment.enroll(user, course_key, check_access=False)
        api._data_api()._update_enrollment(enrollment, is_active=is_active, mode=mode)
    except Exception as err:  # pylint: disable=broad-except
        LOG.warn('API call failed: %s, %s, %s, %s, %s', repr(err), username, course_id, mode, is_active)
        raise APIException(repr(err))
    return enrollment
