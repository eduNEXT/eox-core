"""
Async task for generating reports by executing database queries
and posting the results to the Shipyard API.
"""

import logging

from celery import shared_task
from django.db.utils import DatabaseError, OperationalError

from eox_core.api.data.aggregated_collector.queries import PREDEFINED_QUERIES
from eox_core.api.data.aggregated_collector.utils import execute_query, post_data_to_api, post_process_query_results

logger = logging.getLogger(__name__)

COUNTDOWN = 60
MAX_RETRIES = 3


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
            logger.info("Executing query: %s", query_name)
            try:
                result = execute_query(query_sql)

                processed_result = post_process_query_results(result)
                report_data[query_name] = processed_result
            except (DatabaseError, OperationalError) as e:
                logger.error("Failed to execute query '%s': %s", query_name, e)
                continue

        post_data_to_api(destination_url, report_data, token_generation_url, current_host)

        logger.info("Report generation task completed successfully.")
    except Exception as e:
        logger.error("An error occurred in the report generation task: '%s'. Retrying", e)
        raise self.retry(exc=e, countdown=COUNTDOWN, max_retries=MAX_RETRIES)
