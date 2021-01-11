"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import


class SettingsClass:
    """ dummy settings class """


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_h_v1_test"
    settings.EOX_CORE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.enrollment_h_v1"
    settings.EOX_CORE_PRE_ENROLLMENT_BACKEND = "eox_core.edxapp_wrapper.backends.pre_enrollment_h_v1"
    settings.EOX_CORE_COURSEKEY_BACKEND = "eox_core.edxapp_wrapper.backends.coursekey_h_v1"
    settings.EOX_CORE_CERTIFICATES_BACKEND = "eox_core.edxapp_wrapper.backends.certificates_h_v1_test"
    settings.EOX_CORE_CONFIGURATION_HELPER_BACKEND = "eox_core.edxapp_wrapper.backends.configuration_helpers_h_v1_test"
    settings.EOX_CORE_COURSEWARE_BACKEND = "eox_core.edxapp_wrapper.backends.courseware_h_v1"
    settings.EOX_CORE_GRADES_BACKEND = "eox_core.edxapp_wrapper.backends.grades_h_v1"
    settings.EOX_CORE_MICROSITES_BACKEND = "eox_core.edxapp_wrapper.backends.microsite_configuration_h_v1"
    settings.EOX_CORE_STORAGES_BACKEND = "eox_core.edxapp_wrapper.backends.storages_i_v1_test"
    settings.EOX_CORE_LOAD_PERMISSIONS = False
    settings.DATA_API_DEF_PAGE_SIZE = 1000
    settings.DATA_API_MAX_PAGE_SIZE = 5000
    settings.EOX_CORE_ENABLE_UPDATE_USERS = True
    settings.EOX_CORE_USER_UPDATE_SAFE_FIELDS = ["is_active", "password", "fullname"]
    settings.EOX_CORE_BEARER_AUTHENTICATION = 'eox_core.edxapp_wrapper.backends.bearer_authentication_j_v1_test'


SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)

try:
    import edx_when  # pylint: disable=unused-import
    INSTALLED_APPS += ('eox_core', 'edx_when.apps.EdxWhenConfig')
except ImportError:
    INSTALLED_APPS += ('eox_core',)

ROOT_URLCONF = 'eox_core.urls'
ALLOWED_HOSTS = ['*']

# This key needs to be defined so that the check_apps_ready passes and the
# AppRegistry is loaded
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

ENV_ROOT = '.'

FEATURES = {}
FEATURES['USE_REDIRECTION_MIDDLEWARE'] = True

COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
COURSE_ID_PATTERN = COURSE_KEY_PATTERN.replace('course_key_string', 'course_id')

USERNAME_REGEX_PARTIAL = r'[\w .@_+-]+'
USERNAME_PATTERN = r'(?P<username>{regex})'.format(regex=USERNAME_REGEX_PARTIAL)

PROCTORING_SETTINGS = {
    'LINK_URLS': {
        'contact_us': 'http://test-link.com/contact',
        'faq': 'http://test-link.com/faq',
        'online_proctoring_rules': 'http://test-link.com/rules',
        'tech_requirements': 'http://test-link.com/tech',
    },
    'SITE_NAME': 'test-site-name',
    'PLATFORM_NAME': 'test-platform-name',
}

PROCTORING_BACKENDS = {
    'software_secure': {
        'crypto_key': 'test-key',
        'exam_register_endpoint': 'test-enpoint',
        'exam_sponsor': 'test-sponsor',
        'organization': 'test-org',
        'secret_key': 'test-secret-key',
        'secret_key_id': 'test-secret-key-id',
        'software_download_url': 'http://test.com/url',
    },
    'DEFAULT': 'software_secure',
}
