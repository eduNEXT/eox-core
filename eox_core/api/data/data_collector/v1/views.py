import logging
import requests
import yaml
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from eox_core.api.data.data_collector.tasks import generate_report

from rest_framework.permissions import BasePermission
from rest_framework.authentication import get_authorization_header
from django.conf import settings
from eox_core.api.data.data_collector.v1.serializers import DataCollectorSerializer

logger = logging.getLogger(__name__)


class DatacollectorPermission(BasePermission):
    """
    Permission class to allow access only if the request contains a valid GitHub Action token.
    """
    def has_permission(self, request, view):
        auth_header = get_authorization_header(request).decode('utf-8')
        auth_token = settings.EOX_CORE_DATA_COLLECT_AUTH_TOKEN
        if auth_header and auth_header == f"Bearer {auth_token}":
            return True
        return False


class DataCollectorView(APIView):
    """
    API view to handle data collection requests.

    This view:
    - Validates input using DataCollectorSerializer.
    - Triggers an async task to execute queries and send results to a specified destination.
    """
    # Allow JWT Auth
    permission_classes = [DatacollectorPermission]

    def post(self, request):
        """
        Handles POST requests to collect data.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            Response: A success or error message.
        """
        serializer = DataCollectorSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            query_file_content = validated_data.get("query_file_content")
            query_file_url = validated_data.get("query_file_url")
            destination_url = validated_data.get("destination_url")
            token_generation_url = validated_data.get("token_generation_url")
            current_host = request.get_host() #Remove trailing slash and http

            # If the query file content is not provided, fetch it from the URL
            if not query_file_content and query_file_url:
                try:
                    response = requests.get(query_file_url)
                    if response.status_code == 200:
                        query_file_content = response.text
                    else:
                        return Response(
                            {"error": "Failed to fetch query file from the provided URL."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception as e:
                    return Response(
                        {"error": f"An error occurred while fetching the query file: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            generate_report.delay(destination_url, query_file_content, token_generation_url, current_host)
            return Response(
                {"message": "Data collection task has been initiated successfully."},
                status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
