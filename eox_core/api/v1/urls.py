""" urls.py """

from django.conf import settings
from django.conf.urls import url

from eox_core.api.v1 import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    url(r'^enrollment/$', views.EdxappEnrollment.as_view(), name='edxapp-enrollment'),
    url(r'^grade/$', views.EdxappGrade.as_view(), name='edxapp-grade'),
    url(r'^pre-enrollment/$', views.EdxappPreEnrollment.as_view(), name='edxapp-pre-enrollment'),
    url(r'^userinfo/$', views.UserInfo.as_view(), name='edxapp-userinfo'),
]

if getattr(settings, "EOX_CORE_ENABLE_UPDATE_USERS", None):
    urlpatterns += [
        url(r'^update-user/$', views.EdxappUserUpdater.as_view(), name='edxapp-user-updater'),
    ]
