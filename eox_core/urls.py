from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^eox-info$', views.default_view),
]


