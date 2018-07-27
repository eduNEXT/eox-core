""" urls.py """

from django.conf.urls import url
from eox_core import views

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^eox-info$', views.default_view),
]
