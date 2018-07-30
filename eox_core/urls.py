""" urls.py """

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from eox_core import views

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^eox-info$', views.info_view),
    url(r'^userinfo$', views.UserInfoView.as_view()),
]
