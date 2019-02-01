""" urls.py """

from django.conf.urls import url, include
from eox_core.cms.views import simple_view


urlpatterns = [  # pylint: disable=invalid-name
    url(r'^courses$', simple_view),
]
