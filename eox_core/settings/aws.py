"""
Settings for eox_core project meant to be called on the edx-platform/*/envs/aws.py module
"""
from .common import *  # pylint: disable=wildcard-import


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
    settings.DATA_API_DEF_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_DEF_PAGE_SIZE',
        settings.DATA_API_DEF_PAGE_SIZE
    )
    settings.DATA_API_MAX_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_MAX_PAGE_SIZE',
        settings.DATA_API_MAX_PAGE_SIZE
    )
