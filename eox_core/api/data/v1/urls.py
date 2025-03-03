"""
URLs for the Microsite API
"""
from django.urls import include, re_path

from .routers import ROUTER
from .views import CeleryTasksStatus

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^v1/', include((ROUTER.urls, 'eox_core'), namespace='eox-data-api-v1')),
    re_path(r'^v1/tasks/(?P<task_id>.*)$', CeleryTasksStatus.as_view(), name="celery-data-api-tasks"),
    re_path(r'^', include('eox_core.api.data.aggregated_collector.urls', namespace='eox-data-api-collector')),
]
