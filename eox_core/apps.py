# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class EoxCoreConfig(AppConfig):
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
                'test': { 'relative_path': 'settings.test' },
                'common': { 'relative_path': 'settings.common'},
            },
            'cms.djangoapp': {
                'test': { 'relative_path': 'settings.test' },
                'common': { 'relative_path': 'settings.common'},
            },
        },
    }
