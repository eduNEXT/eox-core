"""
Async task for generating reports by executing database queries
and posting the results to the Shipyard API.
"""

from celery import shared_task, Task
from eox_core.api.data.data_collector.utils import execute_query, post_data_to_api, serialize_data
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
def generate_report(self, destination_url, query_file_content, token_generation_url, current_host):
    """
    Async task to generate a report:
    1. Reads queries from the provided query file content.
    2. Executes each query against the database.
    3. Sends the results to the Shipyard API.

    Args:
        self (Task): The Celery task instance.
        query_file_content (str): The content of the query file in YAML format.

    Raises:
        Retry: If an error occurs, the task retries up to 3 times with a 60-second delay.
    """
    try:
        queries = yaml.safe_load(query_file_content).get("queries", [])
        if not queries:
            logger.warning("No queries found in the provided file. Task will exit.")
            return

        report_data = {}
        for query in queries:
            query_name = query.get("name")
            query_sql = query.get("query")
            logger.info(f"Executing query: {query_name}")
            try:
                result = execute_query(query_sql)

                serialized_result = serialize_data(result)
                report_data[query_name] = serialized_result
            except Exception as e:
                logger.error(f"Failed to execute query '{query_name}': {e}")
                continue

        post_data_to_api(destination_url, report_data, token_generation_url, current_host)

        logger.info("Report generation task completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred in the report generation task: {e}. Retrying")
        raise self.retry(exc=e, countdown=60, max_retries=3)
