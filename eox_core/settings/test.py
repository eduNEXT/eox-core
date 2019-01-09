"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import


class SettingsClass(object):
    """ dummy settings class """
    pass


SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)
EOX_CORE_USERS_BACKEND = "eox_core.edxapp_wrapper.backends.users_h_v1_test"
EOX_CORE_CERTIFICATES_BACKEND = "eox_core.edxapp_wrapper.backends.certificates_h_v1_test"


INSTALLED_APPS = (
    'eox_core',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'edx_proctoring',
    'django_filters',
)

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
