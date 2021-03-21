""" urls.py """

from django.conf.urls import url

from eox_core.api.support.v1 import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    url(r'^user/replace-username/$', views.EdxappReplaceUsername.as_view(), name='edxapp-replace-username'),
]
