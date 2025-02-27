"""_"""
from django.urls import path

from eox_core.api.data.aggregated_collector.v1.views import AggregatedCollectorView

# pylint: disable=invalid-name
app_name = "aggregated_collector"

urlpatterns = [
    path("aggregated-collector/", AggregatedCollectorView.as_view(), name="aggregated_collector"),
]
