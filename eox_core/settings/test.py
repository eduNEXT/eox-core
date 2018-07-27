"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals

from .common import *  # pylint: disable=wildcard-import


class SettingsClass(object):
    pass


settings = SettingsClass()
plugin_settings(settings)
vars().update(settings.__dict__)


# This key needs to be defined so that the check_apps_ready passes and the AppRegistry is loaded
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
