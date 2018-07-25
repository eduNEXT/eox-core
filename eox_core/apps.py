# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from plugins.constants import (
    PluginURLs as URLs,
    ProjectType,
    PluginSettings as Settings,
    PluginSignals as Signals,
    SettingsType,
)


class EoxCoreConfig(AppConfig):
    name = 'eox_core'
    verbose_name = "eduNEXT Openedx Extensions"

    # Class attribute that configures and enables this app as a Plugin App.
    plugin_app = {

        # Configuration setting for Plugin URLs for this app.
        URLs.CONFIG: {

            # Configure the Plugin URLs for each project type, as needed.
            ProjectType.CMS: {

                # The namespace to provide to django's urls.include.
                URLs.NAMESPACE: u'eox-core',

                # The regex to provide to django's urls.url.
                # Optional; Defaults to r''.
                URLs.REGEX: r'^eox-core/',

                # The python path (relative to this app) to the URLs module to
                # be plugged into the project.
                # Optional; Defaults to u'urls'.
                URLs.RELATIVE_PATH: u'urls',
            }
        },

        # Configuration setting for Plugin Settings for this app.
        Settings.CONFIG: {

            ProjectType.LMS: {
                SettingsType.AWS: {
                    Settings.RELATIVE_PATH: u'settings.common',
                },
                SettingsType.COMMON: {
                    Settings.RELATIVE_PATH: u'settings.common',
                },
            },
            ProjectType.CMS: {
                SettingsType.AWS: {
                    Settings.RELATIVE_PATH: u'settings.common',
                },
                SettingsType.COMMON: {
                    Settings.RELATIVE_PATH: u'settings.common',
                },
            }
        },

        # Configuration setting for Plugin Signals for this app.
        Signals.CONFIG: {

            # Configure the Plugin Signals for each Project Type, as needed.
            ProjectType.LMS: {

                # The python path (relative to this app) to the Signals module
                # containing this app's Signal receivers.
                # Optional; Defaults to u'signals'.
                Signals.RELATIVE_PATH: u'my_signals',

                # List of all plugin Signal receivers for this app and project
                # type.
                Signals.RECEIVERS: [{

                    # The name of the app's signal receiver function.
                    Signals.RECEIVER_FUNC_NAME: u'on_signal_x',

                    # The full path to the module where the signal is defined.
                    Signals.SIGNAL_PATH: u'path_to_signal_x_module.SignalX',

                    # The value for dispatch_uid to pass to Signal.connect to
                    # prevent duplicate signals.
                    # Optional; Defaults to full path to the signal's receiver
                    # function.
                    Signals.DISPATCH_UID: u'my_app.my_signals.on_signal_x',

                    # The full path to a sender (if connecting to a specific
                    # sender) to be passed to Signal.connect.
                    # Optional; Defaults to None.
                    Signals.SENDER_PATH: u'full_path_to_sender_app.ModelZ',
                }],
            }
        }
    }
