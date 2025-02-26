"""
Utility functions for report generation, including query execution
and integration with the Shipyard API.
"""

import logging
from datetime import datetime
import requests
from django.conf import settings
from django.db import connection
from eox_core.utils import get_access_token

logger = logging.getLogger(__name__)


def execute_query(sql_query):
    """
    Execute a raw SQL query and return the results in a structured format.

    Args:
        sql_query (str): The raw SQL query to execute.

    Returns:
        list or dict: Structured query results.

    Example:
        >>> execute_query("SELECT id, username FROM auth_user WHERE is_active = 1;")
        [
            {"id": 1, "username": "john_doe"},
            {"id": 2, "username": "jane_doe"}
        ]
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        # If the query returns more than one column, return rows as is.
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            if len(columns) == 1:
                return [row[0] for row in rows]  # Return single-column results as a list
            return [dict(zip(columns, row)) for row in rows]  # Multi-column results as a list of dicts
        return rows


def post_process_query_results(data):
    """
    Cleans and processes query results by:
    - Serializing datetime objects into strings.
    - Extracting scalar values from single-item lists.
    - Returning structured data for further use.

    Args:
        data (dict, list, datetime, or scalar): The query result data.

    Returns:
        dict, list, or scalar: The processed query result.
    """
    if isinstance(data, dict):
        return {key: post_process_query_results(value) for key, value in data.items()}
    if isinstance(data, list):
        # If it's a list with one item, return just the item
        if len(data) == 1:
            return post_process_query_results(data[0])
        return [post_process_query_results(item) for item in data]
    if isinstance(data, datetime):
        return data.isoformat()
    return data


def post_data_to_api(api_url, report_data, token_generation_url, current_host):
    """
    Sends the generated report data to the Shipyard API.

    Args:
        report_data (dict): The data to be sent to the Shipyard API.

    Raises:
        Exception: If the API request fails.
    """
    token = get_access_token(
        token_generation_url,
        settings.EOX_CORE_AGGREGATED_DATA_API_CLIENT_ID,
        settings.EOX_CORE_AGGREGATED_DATA_API_CLIENT_SECRET,
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"instance_domain": current_host, "data": report_data}
    response = requests.post(api_url, json=payload, headers=headers, timeout=10)

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise requests.Timeout("The request to Shipyard API timed out.") from exc
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to post data to Shipyard API: {e}")
