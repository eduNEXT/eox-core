""" urls.py """

from django.conf.urls import url
from eox_core.api.v1 import views

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    url(r'^enrollment/$', views.EdxappEnrollment.as_view(), name='edxapp-enrollment'),
    url(r'^pre-enrollment/$', views.EdxappPreEnrollment.as_view(), name='edxapp-pre-enrollment'),
    url(r'^userinfo/$', views.UserInfo.as_view(), name='edxapp-userinfo'),
]
