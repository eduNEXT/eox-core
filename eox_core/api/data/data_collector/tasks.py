"""
Async task for generating reports by executing database queries
and posting the results to the Shipyard API.
"""

from celery import shared_task
from eox_core.api.data.data_collector.utils import execute_query, post_data_to_api, serialize_data, process_query_results
from eox_core.api.data.data_collector.queries import PREDEFINED_QUERIES
import yaml
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_report(self, destination_url, token_generation_url, current_host):
    """
    Async task to generate a report:
    1. Executes all predefined queries.
    2. Sends the results to the Shipyard API.

    Args:
        self (Task): The Celery task instance.
        destination_url (str): URL to send the results.

    Raises:
        Retry: If an error occurs, the task retries up to 3 times with a 60-second delay.
    """
    try:
        report_data = {}
        for query_name, query_sql in PREDEFINED_QUERIES.items():
            logger.info(f"Executing query: {query_name}")
            try:
                result = execute_query(query_sql)

                serialized_result = serialize_data(result)
                processed_result = process_query_results(serialized_result)
                report_data[query_name] = processed_result
            except Exception as e:
                logger.error(f"Failed to execute query '{query_name}': {e}")
                continue

        post_data_to_api(destination_url, report_data, token_generation_url, current_host)

        logger.info("Report generation task completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred in the report generation task: {e}. Retrying")
        raise self.retry(exc=e, countdown=60, max_retries=3)
