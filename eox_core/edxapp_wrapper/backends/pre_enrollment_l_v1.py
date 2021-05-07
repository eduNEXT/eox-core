#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the pre-enrollment (white listings) functionality that works under the open-release/lilac.master tag
"""
# pylint: disable=import-error, protected-access
import logging

from common.djangoapps.student.models import CourseEnrollmentAllowed  # pylint: disable=no-name-in-module
from django.db import IntegrityError
from rest_framework.exceptions import NotFound

from eox_core.edxapp_wrapper.coursekey import get_valid_course_key
from eox_core.edxapp_wrapper.courseware import get_courseware_courses

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
        course_key = get_valid_course_key(course_id)
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
    except Exception:  # pylint: disable=broad-except
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
    pre_enrollment = kwargs.get('pre_enrollment')
    try:
        LOG.info('Deleting regular pre-enrollment for email: %s course_id: %s', pre_enrollment.email, pre_enrollment.course_id)
        pre_enrollment.delete()
    except Exception:  # pylint: disable=broad-except
        raise NotFound('Pre-enrollment not found for email: {} course_id: {}'.format(pre_enrollment.email, pre_enrollment.course_id))


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
        course_key = get_valid_course_key(course_id)
        pre_enrollment = CourseEnrollmentAllowed.objects.get(course_id=course_key, email=email)
        LOG.info('Getting regular pre-enrollment for email: %s course_id: %s', email, course_id)
    except CourseEnrollmentAllowed.DoesNotExist:
        raise NotFound('Pre-enrollment not found for email: {} course_id: {}'.format(email, course_id))
    return pre_enrollment
