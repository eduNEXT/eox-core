""" urls.py """

from django.conf.urls import url
from eox_core.api.v1 import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
    url(r'^enrollment/$', views.EdxappUser.as_view()),
    url(r'^userinfo$', views.UserInfo.as_view()),
]
