"""
URLs for the Microsite API
"""
from django.urls import include, re_path

app_name = 'eox_core'  # pylint: disable=invalid-name


urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^v1/', include('eox_core.api.data.data_collector.v1.urls', namespace='eox-data-api-collector-v1')),
]
