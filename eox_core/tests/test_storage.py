#!/usr/bin/python
"""
Test module for the custom storages
"""
import mock
from django.test import TestCase

from eox_core.storage import DevelopmentStorage, ProductionStorage


class StaticStoragesTest(TestCase):
    """
    Testing the extended storages
    """
    @mock.patch('eox_core.test_utils.TestStorage.url')
    def test_calling_parent_storage_url_method(self, test_url_mock):  # pylint: disable=invalid-name
        """
        Test the case when the storages have to call the url parent method
        """
        test_url_mock.return_value = "/static/images/logo.png"
        instance_storage = ProductionStorage()
        name = "logo.png"
        result = instance_storage.url(name)
        test_url_mock.assert_called_once()
        self.assertEqual(result, "/static/images/logo.png")

        test_url_mock.reset_mock()
        instance_storage = DevelopmentStorage()
        result = instance_storage.url(name)
        test_url_mock.assert_called_once()
        self.assertEqual(result, "/static/images/logo.png")

    @mock.patch('eox_core.test_utils.TestStorage.url')
    def test_returning_absolute_url_asset(self, test_url_mock):  # pylint: disable=invalid-name
        """
        Test the case when the storages don't have to call the url parent method
        """
        instance_storage = ProductionStorage()
        name = "https://example.com/assets/logo.png"
        result = instance_storage.url(name)
        test_url_mock.assert_not_called()
        self.assertEqual(result, name)

        test_url_mock.reset_mock()
        instance_storage = DevelopmentStorage()
        result = instance_storage.url(name)
        test_url_mock.assert_not_called()
        self.assertEqual(result, name)
