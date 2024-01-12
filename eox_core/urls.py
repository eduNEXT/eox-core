""" urls.py """

from django.urls import include, re_path

from eox_core import views
from eox_core.api_schema import docs_ui_view

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    re_path(r'^eox-info$', views.info_view),
    re_path(r'^api/', include('eox_core.api.urls', namespace='eox-api')),
    re_path(r'^data-api/', include('eox_core.api.data.v1.urls', namespace='eox-data-api')),
    re_path(r'^api-docs/$', docs_ui_view, name='apidocs-ui'),
    re_path(r'^tasks-api/', include('eox_core.api.task_dispatcher.v1.urls', namespace='eox-task-api')),
    re_path(r'^support-api/', include('eox_core.api.support.urls', namespace='eox-support-api')),
]
