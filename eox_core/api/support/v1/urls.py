""" urls.py """

from django.urls import re_path

from eox_core.api.support.v1 import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    re_path(r'^user/replace-username/$', views.EdxappReplaceUsername.as_view(), name='edxapp-replace-username'),
    re_path(r'^oauth-application/$', views.OauthApplicationAPIView.as_view(), name='edxapp-oauth-application'),
]
