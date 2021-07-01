"""
Settings for eox-core
"""
from __future__ import absolute_import, unicode_literals

from importlib.util import find_spec

SECRET_KEY = 'a-not-to-be-trusted-secret-key'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'edx_proctoring',
    'django_filters',
    'oauth2_provider',
    'django_countries',
)
EOX_AUDIT_MODEL_APP = 'eox_audit_model.apps.EoxAuditModelConfig'


def plugin_settings(settings):
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_COMMENTS_SERVICE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.comments_service_users_j_v1"
    settings.EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_j_v1"
    settings.EOX_CORE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.enrollment_h_v1"
    settings.EOX_CORE_PRE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.pre_enrollment_h_v1"
    settings.EOX_CORE_CERTIFICATES_BACKEND = "eox_core.edxapp_wrapper.backends.certificates_h_v1"
    settings.EOX_CORE_CONFIGURATION_HELPER_BACKEND = "eox_core.edxapp_wrapper.backends.configuration_helpers_h_v1"
    settings.EOX_CORE_COURSEWARE_BACKEND = "eox_core.edxapp_wrapper.backends.courseware_h_v1"
    settings.EOX_CORE_GRADES_BACKEND = "eox_core.edxapp_wrapper.backends.grades_h_v1"
    settings.EOX_CORE_STORAGES_BACKEND = "eox_core.edxapp_wrapper.backends.storages_i_v1"
    settings.EOX_CORE_ENABLE_STATICFILES_STORAGE = False
    settings.EOX_CORE_STATICFILES_STORAGE = "eox_core.storage.ProductionStorage"
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
    settings.EOX_CORE_APPEND_LMS_MIDDLEWARE_CLASSES = False
    settings.EOX_CORE_ENABLE_UPDATE_USERS = True
    settings.EOX_CORE_USER_UPDATE_SAFE_FIELDS = ["is_active", "password", "fullname", "mailing_address", "year_of_birth", "gender", "level_of_education", "city", "country", "goals", "bio", "phone_number"]
    settings.EOX_CORE_BEARER_AUTHENTICATION = 'eox_core.edxapp_wrapper.backends.bearer_authentication_j_v1'
    settings.EOX_CORE_ASYNC_TASKS = []

    if settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
        settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES = [
            'fetch_from_created_on_site_prop',
            'fetch_from_user_signup_source',
        ]

    # Sentry Integration
    settings.EOX_CORE_SENTRY_INTEGRATION_DSN = None

    # The setting EOX_CORE_SENTRY_IGNORED_ERRORS is a list of rules that defines which exceptions to ignore.
    # An example below:
    # EOX_CORE_SENTRY_IGNORED_ERRORS = [
    #     {
    #         "exc_class": "openedx.core.djangoapps.user_authn.exceptions.AuthFailedError",
    #         "exc_text": ["AuthFailedError.*Email or password is incorrect"]
    #     },
    # ]
    # Every rule support only 2 keys for now:
    # - exc_class: the path to the exception class we want to ignore. It can only be one
    # - exc_text: a list of regex expressions to search on the last traceback frame text of the exception

    # In this example we have only one rule. We are ignoring AuthFailedError exceptions whose traceback text
    # has a match with the regex provided in the exc_text unique element. If exc_text contains more than one
    # regex, the exception is ignored if any of the regex matches the traceback text.
    settings.EOX_CORE_SENTRY_IGNORED_ERRORS = []

    if find_spec('eox_audit_model') and EOX_AUDIT_MODEL_APP not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(EOX_AUDIT_MODEL_APP)
