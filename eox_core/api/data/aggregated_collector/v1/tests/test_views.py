import pytest
from unittest.mock import patch
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from eox_core.api.data.aggregated_collector.tasks import generate_report

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def api_url():
    return "/eox-core/data-api/v1/aggregated-collector/"

@pytest.mark.django_db
class TestAggregatedCollectorView:
    
    @pytest.fixture(autouse=True)
    def setup(settings):
        """Set default values for settings before each test."""
        settings.AGGREGATED_DATA_COLLECTOR_API_ENABLED = True
        settings.EOX_CORE_AGGREGATED_COLLECT_DESTINATION_URL = "https://example.com/destination"
        settings.EOX_CORE_AGGREGATED_COLLECT_TOKEN_URL = "https://example.com/token"
        settings.EOX_CORE_DATA_COLLECT_AUTH_TOKEN = "valid_token"

    def test_endpoint_disabled(self, api_client, api_url):
        """Should return 403 if the API is disabled in settings."""
        settings.AGGREGATED_DATA_COLLECTOR_API_ENABLED = False

        response = api_client.post(api_url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "This endpoint is currently disabled."

    def test_missing_settings(self, api_client, api_url):
        """Should return 500 if required settings are missing."""
        settings.EOX_CORE_AGGREGATED_COLLECT_DESTINATION_URL = None
        settings.EOX_CORE_AGGREGATED_COLLECT_TOKEN_URL = None

        response = api_client.post(api_url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["error"] == "Data collection settings are not properly configured."

    @patch("eox_core.api.data.aggregated_collector.tasks.generate_report.delay")
    def test_successful_request(self, mock_generate_report, api_client, api_url):
        """Should return 202 and trigger the async task correctly."""
        response = api_client.post(api_url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["message"] == "Data collection task has been initiated successfully."
        mock_generate_report.assert_called_once_with(
            "https://example.com/destination",
            "https://example.com/token",
            "testserver"
        )

    def test_unauthorized_request(self, api_client, api_url):
        """Should return 403 if no authentication token is provided."""
        response = api_client.post(api_url, HTTP_AUTHORIZATION="")

        assert response.status_code == status.HTTP_403_FORBIDDEN
