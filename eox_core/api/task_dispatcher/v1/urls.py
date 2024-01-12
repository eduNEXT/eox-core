"""
Task dispatcher api urls
"""
from django.urls import re_path

from eox_core.api.task_dispatcher.v1.views import TaskAPI

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [
    re_path(r'^v1/tasks/$', TaskAPI.as_view(), name='task-api'),
]
