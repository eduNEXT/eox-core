"""
Courses definitions.
"""

from importlib import import_module
from django.conf import settings


def get_courses_accessible_to_user(*args, **kwargs):
    """ Gets the _courses_accessible_to_user function. """

    backend_function = settings.EOX_CORE_COURSES_BACKEND
    backend = import_module(backend_function)

    return backend.courses_accessible_to_user(*args, **kwargs)


def get_process_courses_list(*args, **kwargs):
    """ Gets the _process_courses_list function. """

    backend_function = settings.EOX_CORE_COURSES_BACKEND
    backend = import_module(backend_function)

    return backend.get_process_courses_list(*args, **kwargs)


def get_course_settings_fields():
    """ Gets course settings fields. """

    backend_function = settings.EOX_CORE_COURSES_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_settings_fields()


def get_course_details_fields():
    """ Gets course details fields. """

    backend_function = settings.EOX_CORE_COURSES_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_details_fields()
