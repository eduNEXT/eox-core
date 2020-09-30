""" urls.py """

from django.conf.urls import url

from eox_core.cms.views import course_team, get_courses_by_course_regex, management_view

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^courses$', management_view, name='management-courses-view'),
    url(r'^course-team-management$', course_team, name='course-team-management'),
    url(r'^get_courses/?$', get_courses_by_course_regex, name='get-courses-regex'),
]
