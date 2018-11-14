"""
URLs for the Microsite API
"""
from django.conf.urls import url, include

from .routers import ROUTER
from .views import CeleryTasksStatus


urlpatterns = [
    url(r'^data-api/v1/', include(ROUTER.urls, namespace='eox-data-api-v1')),
    url(r'^data-api/v1/tasks/(?P<task_id>.*)$', CeleryTasksStatus.as_view(), name="celery-data-api-tasks"),
]
