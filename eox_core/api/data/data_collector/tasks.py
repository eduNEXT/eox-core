"""
Async task for generating reports by executing database queries
and posting the results to the Shipyard API.
"""

from celery import shared_task, Task
from eox_core.api.data.data_collector.utils import execute_query, post_data_to_api, serialize_data, process_query_results
from eox_core.api.data.data_collector.queries import PREDEFINED_QUERIES
import yaml
import logging

logger = logging.getLogger(__name__)


class ReportTask(Task):
    """
    Custom task class to handle report generation with an on_failure hook.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Called when the task has exhausted all retries.

        Args:
            exc (Exception): The exception raised.
            task_id (str): The ID of the failed task.
            args (tuple): The positional arguments for the task.
            kwargs (dict): The keyword arguments for the task.
            einfo (ExceptionInfo): Exception information.
        """
        logger.error(f"Task {task_id} failed after retries. Exception: {exc}. Could not collect data.")


@shared_task(bind=True)
def generate_report(self, destination_url, token_generation_url, current_host):
    """
    Async task to generate a report:
    1. Executes all predefined queries.
    2. Sends the results to the Shipyard API.

    Args:
        self (Task): The Celery task instance.
        destination_url (str): URL to send the results.
        token_generation_url (str): URL to get the access token.
        current_host (str): The host making the request.

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
