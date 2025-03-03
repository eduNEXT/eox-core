"""
URL configuration for the Microsite API.

This module defines the URL patterns for the Microsite API,
including versioned endpoints for aggregated_collector.
"""
from django.urls import include, re_path

app_name = 'eox_core'  # pylint: disable=invalid-name


urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^v1/', include('eox_core.api.data.aggregated_collector.v1.urls', namespace='eox-data-api-collector-v1')),
]
