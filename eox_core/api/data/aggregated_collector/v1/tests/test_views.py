from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from eox_core.api.data.aggregated_collector.utils import execute_query
from eox_core.api.data.aggregated_collector.tasks import generate_report
from eox_core.api.data.aggregated_collector.v1.views import AggregatedCollectorView

class AggregatedCollectorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/eox-core/data-api/v1/aggregated-collector/"
        settings.AGGREGATED_DATA_COLLECTOR_API_ENABLED = True
        settings.EOX_CORE_AGGREGATED_COLLECT_DESTINATION_URL = "http://mock-api.com"
        settings.EOX_CORE_AGGREGATED_COLLECT_TOKEN_URL = "http://mock-token.com"
        settings.EOX_CORE_AGGREGATED_COLLECT_AUTH_TOKEN = "test-token"

    @patch("eox_core.api.data.aggregated_collector.utils.connection.cursor")
    def test_execute_query(self, mock_cursor):
        mock_cursor.return_value.__enter__.return_value.fetchall.return_value = [(1, "test_user")]
        mock_cursor.return_value.__enter__.return_value.description = [("id",), ("username",)]
        
        result = execute_query("SELECT id, username FROM auth_user;")
        self.assertEqual(result, [{"id": 1, "username": "test_user"}])

    @patch("eox_core.api.data.aggregated_collector.tasks.execute_query")
    @patch("eox_core.api.data.aggregated_collector.tasks.post_data_to_api")
    def test_generate_report(self, mock_post, mock_execute):
        mock_execute.return_value = [{"id": 1, "data": "sample"}]
        generate_report("http://mock-api.com", "http://mock-token.com", "localhost")
        mock_post.assert_called_once()

    @patch("eox_core.api.data.aggregated_collector.v1.views.generate_report.delay")
    def test_aggregated_collector_view(self, mock_task):
        response = self.client.post(self.url, HTTP_AUTHORIZATION=f"Bearer {settings.EOX_CORE_AGGREGATED_COLLECT_AUTH_TOKEN}")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_task.assert_called_once()
