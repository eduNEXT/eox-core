"""
Grades definitions.
"""

from importlib import import_module

from django.conf import settings


def get_course_grade_factory():
    """ Gets the CourseGradeFactory object. """

    backend_function = settings.EOX_CORE_GRADES_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_grade_factory()
