#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the pre-enrollment (white listings) functionality that works under the open-release/hawthorn.beta1 tag
"""
# pylint: disable=import-error, protected-access
from __future__ import absolute_import, unicode_literals

import logging

from django.db import IntegrityError
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from rest_framework.exceptions import APIException

from eox_core.edxapp_wrapper.backends.edxfuture_i_v1 import get_program
from eox_core.edxapp_wrapper.backends.enrollment_h_v1 import _validate_org, get_preferred_course_run
from student.models import (
    CourseEnrollmentAllowed,
)

LOG = logging.getLogger(__name__)


def create_pre_enrollment(*args, **kwargs):
    """
    Create pre-enrollment of given user in the course provided.

    Example:
        >>>create_pre_enrollment(
            {
            "email": "bob@example.com",
            "course_id": course-v1-edX-DemoX-1T2015",
            "auto_enroll": "False"
            }
        )
    """
    kwargs = dict(kwargs)
    program_uuid = kwargs.pop('bundle_id', None)
    course_id = kwargs.pop('course_id', None)

    if program_uuid:
        return pre_enroll_on_program(program_uuid, *args, **kwargs)

    return pre_enroll_on_course(course_id=course_id, *args, **kwargs)

def update_pre_enrollment(*args, **kwargs):
    """
    Update pre-enrollment of given user in the course provided.

    Example:
        >>>update_pre_enrollment(
            {
            "email": "bob@example.com",
            "course_id": course-v1-edX-DemoX-1T2015",
            "auto_enroll": "False"
            }
        )
    """
    kwargs = dict(kwargs)
    errors = []
    email = kwargs.get('email')
    auto_enroll = kwargs.pop('auto_enroll', True)
    course_id = kwargs.pop('course_id')
    try:
        course_key = CourseKey.from_string(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.get(course_id=course_key, **kwargs)
        pre_enrollment.auto_enroll = auto_enroll
        pre_enrollment.save()
        LOG.info('Updating regular pre-enrollment for email: %s course_id: %s auto_enroll: %s', email, course_id, auto_enroll)
    except IntegrityError:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    except CourseEnrollmentAllowed.DoesNotExist:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    return pre_enrollment, errors

def delete_pre_enrollment(*args, **kwargs):
    """
    Delete pre-enrollment of given user in the course provided.

    Example:
        >>>delete_pre_enrollment(
            {
            "email": "bob@example.com",
            "course_id": course-v1-edX-DemoX-1T2015"
            }
        )
    """
    kwargs = dict(kwargs)
    errors = []
    email = kwargs.get('email')
    course_id = kwargs.pop('course_id')
    try:
        course_key = CourseKey.from_string(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.get(course_id=course_key, email=email)
        pre_enrollment.delete()
        LOG.info('Deleting regular pre-enrollment for email: %s course_id: %s', email, course_id)
    except IntegrityError:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    except CourseEnrollmentAllowed.DoesNotExist:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    return errors


def get_pre_enrollment(*args, **kwargs):
    """
    Get pre-enrollment of given user in the course provided.

    Example:
        >>>get_pre_enrollment(
            {
            "email": "bob@example.com",
            "course_id": course-v1-edX-DemoX-1T2015"
            }
        )
    """
    kwargs = dict(kwargs)
    errors = []
    email = kwargs.get('email')
    course_id = kwargs.pop('course_id')
    try:
        course_key = CourseKey.from_string(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.get(course_id=course_key, email=email)
        LOG.info('Getting regular pre-enrollment for email: %s course_id: %s', email, course_id)
    except IntegrityError:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    except CourseEnrollmentAllowed.DoesNotExist:
        return None, 'Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id)
    return pre_enrollment, errors

def pre_enroll_on_course(*args, **kwargs):
    """
    Pre-enroll user on a single course
    """
    errors = []
    email = kwargs.get('email')
    auto_enroll = kwargs.get('auto_enroll', True)
    course_id = kwargs.pop('course_id')
    try:
        course_key = CourseKey.from_string(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.create(course_id=course_key, **kwargs)
        LOG.info('Creating regular pre-enrollment for email: %s course_id: %s auto_enroll: %s', email, course_id, auto_enroll)
    except IntegrityError:
        return None, 'Pre-enrollment already exists for email: {} course_id: {}'.format(email, course_id)
    return pre_enrollment, errors


def pre_enroll_on_program(program_uuid, *arg, **kwargs):
    """
    Pre-enroll user on each of the courses of a progam
    """
    results = []
    errors = []
    LOG.info('Pre-enrolling on program: %s', program_uuid)
    try:
        data = get_program(program_uuid)
    except Exception as err:  # pylint: disable=broad-except
        raise APIException(repr(err))
    if not data['courses']:
        raise APIException("No courses found for this program")
    for course in data['courses']:
        if course['course_runs']:
            course_run = get_preferred_course_run(course)
            LOG.info('Pre-enrolling on course_run: %s', course_run['key'])
            course_id = course_run['key']
            result, errors_list = pre_enroll_on_course(course_id=course_id, *arg, **kwargs)
            results.append(result)
            errors.append(errors_list)
        else:
            raise APIException("No course runs available for this course")
    return results, errors


def validate_pre_enrollment(*args, **kwargs):
    """
    Validate pre_enrollment fields
    """
    errors = []
    course_id = kwargs.get("course_id")
    program_uuid = kwargs.get('bundle_id')

    if program_uuid and course_id:
        return None, ['You have to provide a course_id or bundle_id but not both']
    if course_id:
        try:
            if not _validate_org(course_id):
                errors.append('Enrollment not allowed for given org')
        except InvalidKeyError:
            raise APIException("No valid course_id {}".format(course_id))
    return errors
