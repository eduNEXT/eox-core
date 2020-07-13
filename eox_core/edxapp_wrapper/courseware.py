"""
Courseware definitions.
"""

from importlib import import_module

from django.conf import settings


def get_courseware_courses():
    """ Gets courses. """

    backend_function = settings.EOX_CORE_COURSEWARE_BACKEND
    backend = import_module(backend_function)

    return backend.get_courseware_courses()
