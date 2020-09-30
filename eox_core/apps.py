# -*- coding: utf-8 -*-
""" Configuration as explained on tutorial
github.com/edx/edx-platform/tree/master/openedx/core/djangoapps/plugins"""
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
