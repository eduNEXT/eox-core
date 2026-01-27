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
        Import handlers to register signal receivers via @receiver decorators.
        """
        from eox_core import handlers  # pylint: disable=import-outside-toplevel, unused-import  # noqa: F401

    def ready(self):
        """
        Register signal receivers when Django starts.
        """
        from eox_core import handlers  # pylint: disable=import-outside-toplevel, unused-import
        handlers.connect_signals()


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
