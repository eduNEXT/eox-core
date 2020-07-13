"""
Backend for contenstore courses.
"""

from contentstore.views.course import (  # pylint: disable=import-error
    _process_courses_list,
    get_courses_accessible_to_user,
)
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # pylint: disable=import-error
from openedx.core.djangoapps.models.course_details import CourseDetails  # pylint: disable=import-error


def courses_accessible_to_user(*args, **kwargs):
    """ get get_courses_accessible_to_user function. """
    return get_courses_accessible_to_user(*args, **kwargs)


def get_process_courses_list(*args, **kwargs):
    """ get _process_courses_list function. """
    return _process_courses_list(*args, **kwargs)


def get_course_details_fields():
    """ get CourseDetails fields. """
    course_details = CourseDetails(org=None, course_id=None, run=None)
    all_fields = vars(course_details)

    return all_fields.keys()


def get_first_course_key():
    """
    Returns the course key of any course in order to get
    the advance settings keys to populate the course settings
    tab in the Course management view.
    """

    course = CourseOverview.objects.all()[:1]
    if course:
        course_location = course[0].location
    else:
        return ''
    return course_location.course_key
