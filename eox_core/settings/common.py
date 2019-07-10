"""
Settings for eox-core
"""
from __future__ import absolute_import, unicode_literals


SECRET_KEY = 'a-not-to-be-trusted-secret-key'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'edx_proctoring',
    'django_filters',
)


def plugin_settings(settings):
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_h_v1"
    settings.EOX_CORE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.enrollment_h_v1"
    settings.EOX_CORE_PRE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.pre_enrollment_h_v1"
    settings.EOX_CORE_CERTIFICATES_BACKEND = "eox_core.edxapp_wrapper.backends.certificates_h_v1"
    settings.EOX_CORE_CONFIGURATION_HELPER_BACKEND = "eox_core.edxapp_wrapper.backends.configuration_helpers_h_v1"
    settings.EOX_CORE_COURSEWARE_BACKEND = "eox_core.edxapp_wrapper.backends.courseware_h_v1"
    settings.EOX_CORE_GRADES_BACKEND = "eox_core.edxapp_wrapper.backends.grades_h_v1"
    settings.EOX_CORE_MICROSITES_BACKEND = "eox_core.edxapp_wrapper.backends.microsite_configuration_h_v1"
    settings.EOX_CORE_LOAD_PERMISSIONS = True
    settings.DATA_API_DEF_PAGE_SIZE = 1000
    settings.DATA_API_MAX_PAGE_SIZE = 5000
    settings.EDXMAKO_MODULE = "eox_core.edxapp_wrapper.backends.edxmako_module"
    settings.EOX_CORE_COURSES_BACKEND = "eox_core.edxapp_wrapper.backends.courses_h_v1"
    settings.EOX_CORE_COURSEKEY_BACKEND = "eox_core.edxapp_wrapper.backends.coursekey_h_v1"
    settings.EOX_CORE_SITE_CONFIGURATION = "eox_core.edxapp_wrapper.backends.site_configuration_h_v1"
    settings.EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT = 1000
    settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY = True
    settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES = ['fetch_from_unfiltered_table', ]

    if settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
        settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES = [
            'fetch_from_created_on_site_prop',
            'fetch_from_user_signup_source',
        ]
