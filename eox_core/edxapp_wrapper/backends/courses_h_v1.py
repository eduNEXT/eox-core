"""
Backend for contenstore courses.
"""

from contentstore.views.course import get_courses_accessible_to_user, _process_courses_list
from models.settings.course_metadata import CourseMetadata
from openedx.core.djangoapps.models.course_details import CourseDetails


def courses_accessible_to_user(*args, **kwargs):
    """ get get_courses_accessible_to_user function. """
    return get_courses_accessible_to_user(*args, **kwargs)


def get_process_courses_list(*args, **kwargs):
    """ get _process_courses_list function. """
    return _process_courses_list(*args, **kwargs)


def get_course_settings_fields():
    """ get CourseMetadata fields. """
    settings_fields = CourseMetadata.filtered_list()
    if settings_fields:
        return settings_fields
    return []


def get_course_details_fields():
    """ get CourseDetails fields. """
    course_details = CourseDetails(org=None, course_id=None, run=None)
    all_fields = vars(course_details)

    return all_fields.keys()
