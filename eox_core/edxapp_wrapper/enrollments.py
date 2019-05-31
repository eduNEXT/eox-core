#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Users public function definitions
"""

from importlib import import_module
from django.conf import settings


def create_enrollment(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.create_enrollment(*args, **kwargs)


def update_enrollment(*args, **kwargs):
    """ Update enrollments on edxapp """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.update_enrollment(*args, **kwargs)


def get_enrollment(*args, **kwargs):
    """ Get enrollments on edxapp """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.get_enrollment(*args, **kwargs)


def delete_enrollment(*args, **kwargs):
    """ Delete enrollments on edxapp """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.delete_enrollment(*args, **kwargs)


# pylint: disable=invalid-name
def check_edxapp_enrollment_is_valid(*args, **kwargs):
    """ Checks the db for accounts with the same email or password """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.check_edxapp_enrollment_is_valid(*args, **kwargs)

def validate_org(course_id):
    """
    Validate the course organization against all possible orgs for the site
    """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend._validate_org(course_id)

def get_preferred_course_run(course_id):
    """
    Return the course run most suitable for the enrollment date
    """

    backend_function = settings.EOX_CORE_ENROLLMENT_BACKEND
    backend = import_module(backend_function)

    return backend.get_preferred_course_run(course_id)
