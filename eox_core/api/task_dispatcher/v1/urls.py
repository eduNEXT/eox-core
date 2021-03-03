"""
Task dispatcher api urls
"""
from django.conf.urls import url

from eox_core.api.task_dispatcher.v1.views import TaskAPI

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [
    url(r'^v1/tasks/$', TaskAPI.as_view(), name='task-api'),
]
