"""
Swagger view generator
"""
from django.conf import settings
from django.conf.urls import url
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.openapi import SwaggerDict
from drf_yasg.views import get_schema_view
from edx_api_doc_tools import get_docs_cache_timeout, make_api_info
from rest_framework import permissions

from eox_core.api.v1 import views


class APISchemaGenerator(OpenAPISchemaGenerator):
    """
    Schema generator for eox-core.

    Define an exclusive base path to perform requests for each endpoint and a
    specific security definition using oauth without overwritting project wide
    settings.
    """

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.base_path = '/eox-core/api/v1/'
        return schema

    def get_security_definitions(self):
        security_definitions = {
            'OAuth2': {
                'flow': 'application',
                'tokenUrl': '{}/oauth2/access_token/'.format(settings.LMS_ROOT_URL),
                'type': 'oauth2',
            },
        }
        security_definitions = SwaggerDict.as_odict(security_definitions)
        return security_definitions


api_urls = [  # pylint: disable=invalid-name
    url(r'^enrollment/$', views.EdxappEnrollment.as_view(), name='edxapp-enrollment'),
    url(r'^grade/$', views.EdxappGrade.as_view(), name='edxapp-grade'),
    url(r'^user/$', views.EdxappUser.as_view(), name='edxapp-user'),
]

if getattr(settings, "EOX_CORE_ENABLE_UPDATE_USERS", None):
    api_urls += [
        url(r'^update-user/$', views.EdxappUserUpdater.as_view(), name='edxapp-user-updater'),
    ]

api_info = make_api_info(  # pylint: disable=invalid-name
    title="eox core",
    version="v1",
    email=" contact@edunext.co",
    description="REST APIs to interact with edxapp",
)

docs_ui_view = get_schema_view(  # pylint: disable=invalid-name
    api_info,
    generator_class=APISchemaGenerator,
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=api_urls,
).with_ui('swagger', cache_timeout=get_docs_cache_timeout())
