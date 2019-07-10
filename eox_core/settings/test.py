"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import


class SettingsClass(object):
    """ dummy settings class """
    pass


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
    settings.EOX_CORE_LOAD_PERMISSIONS = False
    settings.DATA_API_DEF_PAGE_SIZE = 1000
    settings.DATA_API_MAX_PAGE_SIZE = 5000


SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)

INSTALLED_APPS += ('eox_core', )

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

FEATURES = {}
FEATURES['USE_REDIRECTION_MIDDLEWARE'] = True

COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
COURSE_ID_PATTERN = COURSE_KEY_PATTERN.replace('course_key_string', 'course_id')

USERNAME_REGEX_PARTIAL = r'[\w .@_+-]+'
USERNAME_PATTERN = r'(?P<username>{regex})'.format(regex=USERNAME_REGEX_PARTIAL)
