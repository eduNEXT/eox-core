""" urls.py """

from django.conf.urls import include, url

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^v1/', include('eox_core.api.v1.urls', namespace='eox-api')),
]
