"""
Views for the Aggregated Collector API (v1).

This module defines the API views for collecting and processing data.
"""

import logging

from django.conf import settings
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

    def post(self, request):
        """
        Handles POST requests to collect data.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            Response: A success or error message.
        """
        if not getattr(settings, "AGGREGATED_DATA_COLLECTOR_API_ENABLED", False):
            return Response(
                {"error": "This endpoint is currently disabled."},
                status=status.HTTP_403_FORBIDDEN
            )

        destination_url = getattr(settings, "EOX_CORE_AGGREGATED_COLLECT_DESTINATION_URL", None)
        token_generation_url = getattr(settings, "EOX_CORE_AGGREGATED_COLLECT_TOKEN_URL", None)

        if not destination_url or not token_generation_url:
            logger.error("Data collection settings are missing.")
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
