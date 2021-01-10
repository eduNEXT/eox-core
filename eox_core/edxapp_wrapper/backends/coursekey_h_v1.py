#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend for the CourseKey validations that works under the open-release/hawthorn.beta1 tag
"""
# pylint: disable=import-error, protected-access
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.site_configuration.helpers import get_all_orgs, get_current_site_orgs
from rest_framework.serializers import ValidationError


def get_valid_course_key(course_id):
    """
    Return the CourseKey if the course_id is valid
    """
    try:
        return CourseKey.from_string(course_id)
    except InvalidKeyError:
        raise ValidationError("Invalid course_id {}".format(course_id))


def validate_org(course_id):
    """
    Validate the course organization against all possible orgs for the site

    To determine if the Org is valid we must look at 3 things
    1 Orgs in the current site
    2 Orgs in other sites
    3 flag EOX_CORE_USER_ENABLE_MULTI_TENANCY
    """

    if not settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
        return True

    course_key = get_valid_course_key(course_id)
    current_site_orgs = get_current_site_orgs() or []

    if not current_site_orgs:  # pylint: disable=no-else-return
        if course_key.org in get_all_orgs():
            return False
        return True
    else:
        return course_key.org in current_site_orgs
