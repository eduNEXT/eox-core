# -*- coding: utf-8 -*-
""" Configuration as explained on tutorial
github.com/openedx/edx-platform/tree/master/openedx/core/djangoapps/plugins"""
from __future__ import unicode_literals

from django.apps import AppConfig


class EoxCoreConfig(AppConfig):
    """App configuration"""
    name = 'eox_core'
    verbose_name = "eduNEXT Openedx Extensions"

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'eox-core',
                'regex': r'^eox-core/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'lms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
                'devstack': {'relative_path': 'settings.devstack'},
            },
        },
    }

    def ready(self):
        """
        Method to perform actions after apps registry is ended
        """
        from eox_core.api.v1.permissions import load_permissions as load_api_permissions  # pylint: disable=import-outside-toplevel

        load_api_permissions()


class EoxCoreCMSConfig(EoxCoreConfig):
    """App configuration"""
    name = 'eox_core'
    verbose_name = "eduNEXT Openedx Extensions"

    plugin_app = {
        'url_config': {
            'cms.djangoapp': {
                'namespace': 'eox-core',
                'regex': r'^eox-core/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'cms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }
