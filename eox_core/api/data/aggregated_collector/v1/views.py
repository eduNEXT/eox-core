"""
Views for the Aggregated Collector API (v1).

This module defines the API views for collecting and processing data.
"""

import logging

from django.conf import settings
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_core.api.data.aggregated_collector.tasks import generate_report
from eox_core.api.data.aggregated_collector.v1.permissions import AggregatedCollectorPermission

logger = logging.getLogger(__name__)


class AggregatedCollectorView(APIView):
    """
    API view to handle data collection requests.

    This feature is **100% opt-in**, meaning that it will only work if explicitly enabled
    by the system administrator. No data is extracted or sent without consent.

    This view:
    - Triggers an async task to execute queries and send results to a specified destination.
    """
    permission_classes = [AggregatedCollectorPermission]

    def post(self, request: HttpRequest) -> Response:
        """
        Handles POST requests to collect data.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            Response: A success or error message.
        """
        destination_url = getattr(settings, "EOX_CORE_AGGREGATED_COLLECTOR_TARGET_URL", None)
        token_generation_url = getattr(settings, "EOX_CORE_AGGREGATED_COLLECTOR_TARGET_TOKEN_URL", None)
        client_id = getattr(settings, "EOX_CORE_AGGREGATED_COLLECTOR_TARGET_CLIENT_ID", None)
        client_secret = getattr(settings, "EOX_CORE_AGGREGATED_COLLECTOR_TARGET_CLIENT_SECRET", None)

        if not all([destination_url, token_generation_url, client_id, client_secret]):
            logger.error("Missing required Aggregated Data Collector settings.")
            return Response(
                {"error": "Data collection settings are not properly configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        current_host = request.get_host()  # Remove trailing slash and http

        generate_report.delay(destination_url, token_generation_url, current_host)
        return Response(
            {"message": "Data collection task has been initiated successfully."},
            status=status.HTTP_202_ACCEPTED
        )
