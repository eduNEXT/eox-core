from django.conf.urls import url
from eox_core import views

urlpatterns = [
    url(r'^eox-info$', views.default_view),
]
