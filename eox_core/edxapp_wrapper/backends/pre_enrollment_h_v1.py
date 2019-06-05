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
from rest_framework.exceptions import APIException, NotFound

from eox_core.edxapp_wrapper.backends.edxfuture_i_v1 import get_program
from eox_core.edxapp_wrapper.enrollments import validate_org, get_preferred_course_run
from eox_core.edxapp_wrapper.courseware import get_courseware_courses
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
    warnings = []
    email = kwargs.get('email')
    auto_enroll = kwargs.get('auto_enroll', False)
    course_id = kwargs.pop('course_id')

    try:
        course_key = get_course_key(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.create(course_id=course_key, **kwargs)
        # Check if the course exists otherwise add a warning
        course = get_courseware_courses().get_course(course_key)
        LOG.info('Creating regular pre-enrollment for email: %s course_id: %s auto_enroll: %s', email, course.id, auto_enroll)
    except IntegrityError:
        pre_enrollment = None
        raise NotFound('Pre-enrollment already exists for email: {} course_id: {}'.format(email, course_id))
    except ValueError:
        warnings = ['Course with course_id:{} does not exist'.format(course_id)]
    return pre_enrollment, warnings

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
    auto_enroll = kwargs.pop('auto_enroll', False)
    pre_enrollment = kwargs.get('pre_enrollment')
    try:
        pre_enrollment.auto_enroll = auto_enroll
        pre_enrollment.save()
        LOG.info('Updating regular pre-enrollment for email: %s course_id: %s auto_enroll: %s', pre_enrollment.email, pre_enrollment.course_id, auto_enroll)
    except Exception: # pylint: disable=broad-except
        raise NotFound('Pre-enrollment not found for email: {} course_id: {}'.format(pre_enrollment.email, pre_enrollment.course_id))
    return pre_enrollment

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
    email = kwargs.get('email')
    course_id = kwargs.get('course_id')
    pre_enrollment = get_pre_enrollment(**kwargs)

    try:
        LOG.info('Deleting regular pre-enrollment for email: %s course_id: %s', email, course_id)
        pre_enrollment.delete()
    except Exception: # pylint: disable=broad-except
        raise NotFound('Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id))

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
    email = kwargs.get('email')
    course_id = kwargs.pop('course_id')
    try:
        course_key = get_course_key(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.get(course_id=course_key, email=email)
        LOG.info('Getting regular pre-enrollment for email: %s course_id: %s', email, course_id)
    except CourseEnrollmentAllowed.DoesNotExist:
        raise NotFound('Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id))
    return pre_enrollment

def pre_enroll_on_program(program_uuid, *arg, **kwargs):
    """
    Pre-enroll user on each of the courses of a progam
    """
    results = []
    LOG.info('Pre-enrolling on program: %s', program_uuid)
    try:
        data = get_program(program_uuid)
    except Exception as err:  # pylint: disable=broad-except
        raise NotFound(repr(err))
    if not data['courses']:
        raise NotFound("No courses found for this program")
    for course in data['courses']:
        if course['course_runs']:
            course_run = get_preferred_course_run(course)
            LOG.info('Pre-enrolling on course_run: %s', course_run['key'])
            course_id = course_run['key']
            try:
                result, warning = create_pre_enrollment(course_id=course_id, *arg, **kwargs)
            except APIException as error:
                results.append({'Error': '{} for course_id:{}'.format(error.detail, course_id)})
            else:
                results.append({'pre_enrollment': result, 'warning': warning})
        else:
            results.append({'Error': 'No course runs available for this course_id {}'.format(course)})
    return results


def get_course_key(course_id):
    """
    Return the CourseKey if the course_id is valid
    """
    try:
        return CourseKey.from_string(course_id)
    except InvalidKeyError:
        raise NotFound("No valid course_id {}".format(course_id))
