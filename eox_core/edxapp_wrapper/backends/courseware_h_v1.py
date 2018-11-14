"""
Backend for courseware module.
"""

from lms.djangoapps.courseware import courses  # pylint: disable=import-error


def get_courseware_courses():
    """ get courses. """
    return courses
