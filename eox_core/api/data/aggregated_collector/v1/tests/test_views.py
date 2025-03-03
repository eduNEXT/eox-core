"""
Test suite for Aggregated Data Collector API.
"""
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from eox_core.api.data.aggregated_collector.tasks import generate_report


class AggregatedCollectorViewTests(TestCase):
    """
    Test cases for the Aggregated Data Collector API.
    """
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("eox-data-api:eox-data-api-collector:eox-data-api-collector-v1:aggregated_collector")
        settings.AGGREGATED_DATA_COLLECTOR_API_ENABLED = True
        settings.EOX_CORE_AGGREGATED_COLLECTOR_TARGET_URL = "http://mock-api.com"
        settings.EOX_CORE_AGGREGATED_COLLECTOR_TARGET_TOKEN_URL = "http://mock-token.com"
        settings.EOX_CORE_AGGREGATED_COLLECTOR_AUTH_TOKEN = "test-token"
        settings.EOX_CORE_AGGREGATED_COLLECTOR_TARGET_CLIENT_ID = "test-client-id"
        settings.EOX_CORE_AGGREGATED_COLLECTOR_TARGET_CLIENT_SECRET = "test-client-secret"

    @patch("eox_core.api.data.aggregated_collector.tasks.execute_query")
    @patch("eox_core.api.data.aggregated_collector.tasks.post_data_to_api")
    def test_generate_report(self, mock_post, mock_execute):
        """
        Test generate_report function to ensure data is retrieved and posted correctly.
        """
        mock_execute.return_value = [{"id": 1, "data": "sample"}]

        generate_report.run("http://mock-api.com", "http://mock-token.com", "localhost")

        mock_post.assert_called_once()

    @patch("eox_core.api.data.aggregated_collector.v1.views.generate_report.delay")
    def test_aggregated_collector_view(self, mock_task):
        """
        Test AggregatedCollectorView to ensure it correctly triggers the report generation task.
        """
        response = self.client.post(self.url, HTTP_AUTHORIZATION=f"Bearer {settings.EOX_CORE_AGGREGATED_COLLECTOR_AUTH_TOKEN}")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        mock_task.assert_called_once()
