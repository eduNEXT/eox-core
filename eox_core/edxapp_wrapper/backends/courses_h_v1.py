"""
Backend for contenstore courses.
"""

from contentstore.views.course import get_courses_accessible_to_user, _process_courses_list


def courses_accessible_to_user(*args, **kwargs):
    """ get get_courses_accessible_to_user function. """
    return get_courses_accessible_to_user(*args, **kwargs)


def get_process_courses_list(*args, **kwargs):
    """ get _process_courses_list function. """
    return _process_courses_list(*args, **kwargs)
