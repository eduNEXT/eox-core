"""
Backend for the Cohorts that works under the open-release/juniper.master tag.
"""
from openedx.core.djangoapps.course_groups.cohorts import get_cohort  # pylint: disable=import-error


def get_user_cohort(*args, **kwargs):
    """
    Function used to get CourseUserGroup (cohort type) for a given course and user.
    """
    return get_cohort(*args, **kwargs)
