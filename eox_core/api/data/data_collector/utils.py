"""
Utility functions for report generation, including query execution
and integration with the Shipyard API.
"""

import yaml
from django.db import connection
import requests
from django.conf import settings
from datetime import datetime
import logging

from eox_core.utils import get_access_token

logger = logging.getLogger(__name__)


def execute_query(sql_query):
    """
    Execute a raw SQL query and return the results in a structured format.
    
    Args:
        sql_query (str): The raw SQL query to execute.
    
    Returns:
        list or dict: Structured query results.
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


def serialize_data(data):
    """
    Recursively serialize data, converting datetime objects to strings.

    Args:
        data (dict or list): The data to serialize.

    Returns:
        dict or list: The serialized data with datetime objects as strings.
    """
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, datetime):
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
        settings.EOX_CORE_SAVE_DATA_API_CLIENT_ID,
        settings.EOX_CORE_SAVE_DATA_API_CLIENT_SECRET,
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"instance_domain":current_host, "data": report_data}
    response = requests.post(api_url, json=payload, headers=headers)

    if not response.ok:
        raise Exception(f"Failed to post data to Shipyard API: {response.content}")
