#!/usr/bin/python
"""
Tests the separation layer between edxapp and the plugin
"""
from django.test import TestCase
from mock import Mock, patch

from eox_core.edxapp_wrapper import configuration_helpers


class ConfigurationHelpersTest(TestCase):
    """
    Making sure that the configuration_helpers backend works
    """

    @patch('eox_core.edxapp_wrapper.configuration_helpers.import_module')
    def test_imported_module_is_used(self, import_mock):
        """
        Testing the backend is imported and used
        """
        backend = Mock()
        import_mock.side_effect = backend

        configuration_helpers.get_configuration_helper()

        import_mock.assert_called()
        backend.assert_called()
