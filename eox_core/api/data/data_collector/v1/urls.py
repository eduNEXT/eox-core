"""_"""
from django.urls import path
from eox_core.api.data.data_collector.v1.views import DataCollectorView

app_name = "data_collector"

urlpatterns = [
    path("collect-data/", DataCollectorView.as_view(), name="collect_data"),
]
