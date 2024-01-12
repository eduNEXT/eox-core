""" urls.py """

from django.conf import settings
from django.urls import re_path

from eox_core.api.v1 import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    re_path(r'^enrollment/$', views.EdxappEnrollment.as_view(), name='edxapp-enrollment'),
    re_path(r'^grade/$', views.EdxappGrade.as_view(), name='edxapp-grade'),
    re_path(r'^pre-enrollment/$', views.EdxappPreEnrollment.as_view(), name='edxapp-pre-enrollment'),
    re_path(r'^userinfo/$', views.UserInfo.as_view(), name='edxapp-userinfo'),
]

if getattr(settings, "EOX_CORE_ENABLE_UPDATE_USERS", None):
    urlpatterns += [
        re_path(r'^update-user/$', views.EdxappUserUpdater.as_view(), name='edxapp-user-updater'),
    ]
