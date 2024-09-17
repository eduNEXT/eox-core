"""
Test module for the Task dispatcher API
"""
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from mock import MagicMock, patch
from rest_framework import status
from rest_framework.test import APIClient

from eox_core.api.task_dispatcher.v1.views import TaskAPI


@override_settings(EOX_CORE_ASYNC_TASKS=["dummy.task.path.task_name"])
class TestTaskAPI(TestCase):
    """ Tests for the task dispatcher API """

    patch_permissions = patch(
        "rest_framework.permissions.IsAdminUser.has_permission",
        return_value=True,
    )

    def setUp(self):
        """setup fixtures"""
        self.api_user = User(1, "test@example.com", "test")
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)
        self.url = reverse("eox-task-api:task-api")

    @patch("celery.current_app.AsyncResult")
    @patch_permissions
    def test_get_task_statuses(self, _, m_async_result):
        """Test that the GET method works with default parameters"""
        m_async_result.return_value.status = "READY"
        m_async_result.return_value.result = "result"
        m_async_result.return_value.ready.return_value = True
        expected_response = {"result": "result", "status": "READY"}

        response = self.client.get(self.url, data={"id": "2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch.object(TaskAPI, "import_task")
    @patch("celery.current_app")
    @patch('eox_core.api.task_dispatcher.v1.views.get_current_site')
    @patch_permissions
    def test_post_valid_task(self, _, m_site, m_current_app, m_task_function):
        """
        Test that the POST method works for a task that is enabled in the
        EOX_CORE_ASYNC_TASKS setting and registered in the worker
        """
        result = MagicMock()
        result.id = "70-421"
        m_task_function.return_value.delay.return_value = result
        m_current_app.tasks = ["dummy.task.path.task_name"]
        m_site.id = 1
        params = {
            "task_path": "dummy.task.path.task_name",
            "task_params": {},
        }
        expected_response = {"task_id": result.id}

        response = self.client.post(self.url, data=params, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @patch("celery.current_app")
    @patch('eox_core.api.task_dispatcher.v1.views.get_current_site')
    @patch_permissions
    def test_post_disabled_task(self, _, m_site, m_current_app):
        """
        Test that the POST method fails for a task that is registered in the
        in the worker and is disabled in EOX_CORE_ASYNC_TASKS.
        """
        m_current_app.tasks = ["dummy.task.path.task_name2"]
        m_site.id = 1
        params = {
            "task_path": "dummy.task.path.task_name2",
            "task_params": {},
        }
        expected_response = {"detail": "Invalid task path"}

        response = self.client.post(self.url, data=params, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)

    @patch("celery.current_app")
    @patch('eox_core.api.task_dispatcher.v1.views.get_current_site')
    @patch_permissions
    def test_post_unregistered_task(self, _, m_site, m_current_app):
        """
        Test that the POST method fails for a task that is enabled in
        EOX_CORE_ASYNC_TASKS and is **not** registered in the worker
        """
        m_current_app.tasks = ["dummy.task.path.task_name2"]
        m_site.id = 1
        params = {
            "task_path": "dummy.task.path.task_name",
            "task_params": {},
        }
        expected_response = {"detail": "Invalid task path"}

        response = self.client.post(self.url, data=params, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected_response)
