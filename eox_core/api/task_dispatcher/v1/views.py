"""
View for the tasks dispatcher API
"""
import logging
from importlib import import_module

import celery
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication

try:
    from eox_audit_model.decorators import audit_drf_api
except ImportError:
    def audit_drf_api(*args, **kwargs):
        """Identity decorator"""
        return lambda x: x

LOG = logging.getLogger(__name__)


class TaskAPI(APIView):
    """
    Celery task dispatcher API
    """

    authentication_classes = [BearerAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Check the status of a celery task given an id.

            GET /eox-core/tasks-api/v1/tasks/{id}

        parameters:
            task_id(path): task identifier

        example response:
            {
            "result": {"updated_emails": 23},
            "status": "READY
            }
        """
        params = request.query_params
        task_id = params.get("id")

        if not task_id:
            return Response({"detail": "Task id needed"}, status=HTTP_400_BAD_REQUEST)

        async_result = celery.current_app.AsyncResult(id=task_id)

        result = async_result.result if async_result.ready() else {}

        return Response({"result": str(result), "status": str(async_result.status)})

    @audit_drf_api(action='eox-core Task dispatcher.', method_name='eox_core_api_method')
    def post(self, request):
        """
        Dispatches a task to a celery worker. The task must be registered in the worker
        and have to be enabled in the setting EOX_CORE_ASYNC_TASKS.

        Some async task require context from the original request, if a key 'context'
        is included in the task_parameters the site id will be added as a value.
        Original values will be discarded.

            POST /eox-core/tasks-api/v1/tasks/

        parameters:
            task_path(body): Full path to the task
            task_parameters(body): Dictionary with the keyword arguments of the task
            and their values.

        example body:
            {
                "task_path": "path.to.example.task"
                "task_params" {
                    "email": "johndoe@email.com"
                    "username": "john_doe"
                }
            }

        example response:
            { task_id: "7faf4b00-b526-4787-8ef2-f543dadfdb09" }
        """
        data = request.data
        task_path = data.get("task_path", "")
        task_parameters = data.get("task_parameters", {})
        site_id = get_current_site(request).id

        if "context" in task_parameters:
            task_parameters['context'] = {"site_id": site_id}
        enabled_tasks = settings.EOX_CORE_ASYNC_TASKS

        registered_tasks = celery.current_app.tasks

        if task_path not in enabled_tasks or task_path not in registered_tasks:
            return Response({"detail": "Invalid task path"}, status=HTTP_404_NOT_FOUND)

        task = self.import_task(task_path)

        if task:
            result = task.delay(**task_parameters)
            LOG.info("Task %s with params %s", task_path, task_parameters)
            return Response({"task_id": result.id})

        return Response({"detail": "Module not found"}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def import_task(task_fullpath):
        """
        Given the full path to the function in dot notation import
        the module and return the function reference
        """
        module_path, task_name = task_fullpath.rsplit(".", 1)
        try:
            module = import_module(module_path)
            return getattr(module, task_name)
        except ImportError:
            LOG.error("ImportError while importing %s", module_path)
            return None
        except AttributeError:
            LOG.error("AttributeError while importing %s", task_name)
            return None
