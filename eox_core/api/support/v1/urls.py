""" urls.py """

from django.conf.urls import url

from eox_core.api.support.v1 import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
]
