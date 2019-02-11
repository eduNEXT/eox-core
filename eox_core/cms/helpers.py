"""
Helpers module.
"""

import waffle

from django.http import HttpResponseNotFound


ENABLE_COURSE_MANAGEMENT_AUTOMATION = 'course_management_automation_module'


def enable_course_management_view(function):
    """
    A decorator to check if the waffle switch is active and
    the course management view can be accessed.
    """
    def wrap(request, *args, **kwargs):
        if not waffle.switch_is_active(ENABLE_COURSE_MANAGEMENT_AUTOMATION):
            return HttpResponseNotFound()
        else:
            return function(request, *args, **kwargs)
    return wrap
