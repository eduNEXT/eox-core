"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals


SECRET_KEY = 'a-not-to-be-trusted-secret-key'


def plugin_settings(settings):
    """
    Defines eox-core settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_USER_CREATION_BACKEND = "eox_core.edxapp_wrapper.backends.users_h_v1"
