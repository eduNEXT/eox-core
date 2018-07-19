from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.default_view),
    # url(r'^something/$', 'something_view'),
]


