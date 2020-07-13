#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CourseKey public function definitions
"""

from importlib import import_module

from django.conf import settings


def get_valid_course_key(course_id):
    """
    Return a valid CourseKey for the given course_id
    """

    backend_function = settings.EOX_CORE_COURSEKEY_BACKEND
    backend = import_module(backend_function)

    return backend.get_valid_course_key(course_id)


def validate_org(course_id):
    """
    Return a valid CourseKey for the given course_id
    """

    backend_function = settings.EOX_CORE_COURSEKEY_BACKEND
    backend = import_module(backend_function)

    return backend.validate_org(course_id)
