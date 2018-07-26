"""
Settings for eox-core
"""

from __future__ import absolute_import, unicode_literals
from .common import plugin_settings as common_settings


def plugin_settings(settings):
    """
    Defines completion-specific settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    common_settings(settings)

    settings.EOX_CORE_USER_CREATION_BACKEND = "eox_core.edxapp_wrapper.tests.users_backend"
