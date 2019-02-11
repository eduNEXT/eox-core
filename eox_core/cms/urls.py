""" urls.py """

from django.conf.urls import url, include
from eox_core.cms.views import management_view, course_team, get_all_orgs


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^courses$', management_view, name='management-courses-view'),
    url(r'^course-team-management$', course_team, name='course-team-management'),
    url(r'^get_all_orgs$', get_all_orgs, name='get-all-orgs'),
]
