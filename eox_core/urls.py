""" urls.py """

from django.conf.urls import include, url

from eox_core import views

app_name = 'eox_core'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^eox-info$', views.info_view),
    url(r'^api/', include('eox_core.api.urls', namespace='eox-api')),
    url(r'^data-api/', include('eox_core.api.data.v1.urls', namespace='eox-data-api')),
    url(r'^management/', include('eox_core.cms.urls', namespace='eox-course-management')),
]
