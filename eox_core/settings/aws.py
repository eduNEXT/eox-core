"""
Settings for eox_core project meant to be called on the edx-platform/*/envs/aws.py module
"""
from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_USERS_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USERS_BACKEND',
        settings.EOX_CORE_USERS_BACKEND
    )
    settings.EOX_CORE_ENROLLMENT_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_ENROLLMENT_BACKEND',
        settings.EOX_CORE_ENROLLMENT_BACKEND
    )
    settings.EOX_CORE_PRE_ENROLLMENT_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_PRE_ENROLLMENT_BACKEND',
        settings.EOX_CORE_PRE_ENROLLMENT_BACKEND
    )
    settings.EOX_CORE_CERTIFICATES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_CERTIFICATES_BACKEND',
        settings.EOX_CORE_CERTIFICATES_BACKEND
    )
    settings.EOX_CORE_COURSEWARE_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSEWARE_BACKEND',
        settings.EOX_CORE_COURSEWARE_BACKEND
    )
    settings.EOX_CORE_GRADES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_GRADES_BACKEND',
        settings.EOX_CORE_GRADES_BACKEND
    )
    settings.EOX_CORE_MICROSITES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_MICROSITES_BACKEND',
        settings.EOX_CORE_MICROSITES_BACKEND
    )
    settings.EOX_CORE_LOAD_PERMISSIONS = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_LOAD_PERMISSIONS',
        settings.EOX_CORE_LOAD_PERMISSIONS
    )
    settings.DATA_API_DEF_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_DEF_PAGE_SIZE',
        settings.DATA_API_DEF_PAGE_SIZE
    )
    settings.DATA_API_MAX_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_MAX_PAGE_SIZE',
        settings.DATA_API_MAX_PAGE_SIZE
    )
    settings.EDXMAKO_MODULE = getattr(settings, 'ENV_TOKENS', {}).get(
        'EDXMAKO_MODULE',
        settings.EDXMAKO_MODULE
    )
    settings.EOX_CORE_COURSES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSES_BACKEND',
        settings.EOX_CORE_COURSES_BACKEND
    )
    settings.EOX_CORE_COURSEKEY_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSEKEY_BACKEND',
        settings.EOX_CORE_COURSEKEY_BACKEND
    )
    settings.EOX_CORE_SITE_CONFIGURATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_SITE_CONFIGURATION',
        settings.EOX_CORE_SITE_CONFIGURATION
    )
    settings.EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT',
        settings.EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT
    )

    settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USER_ENABLE_MULTI_TENANCY',
        settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY
    )
    if not settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
        user_origin_sources = [
            'fetch_from_unfiltered_table',
        ]
    else:
        user_origin_sources = settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES
    settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USER_ORIGIN_SITE_SOURCES',
        user_origin_sources
    )

    if settings.SERVICE_VARIANT == "lms":
        settings.MIDDLEWARE_CLASSES += [
            'eox_core.middleware.PathRedirectionMiddleware',
            'eox_core.middleware.RedirectionsMiddleware'
        ]
