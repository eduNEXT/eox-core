# -*- coding: utf-8 -*-
""" . """
from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient


class TestEnrollmentsAPI(TestCase):
    """ Tests for the enrollments endpoints """

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """ setup """
        super(TestEnrollmentsAPI, self).setUp()
        self.api_user = User('test', 'test@example.com', 'test')
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)

    @patch_permissions
    def test_api_get_validation(self, _):
        """ Test that the GET method requires some parameters """
        response = self.client.get('/api/v1/enrollment/')

        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data[0])

        params = {
            'course_id': 'course-v1:org+course+run',
        }
        response = self.client.get('/api/v1/enrollment/', params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data[0])

    @patch('eox_core.api.v1.views.get_enrollment')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch_permissions
    def test_api_get(self, _, m_get_user, m_get_enrollment):
        """ Test that the GET method works under normal conditions """
        m_get_user.return_value.username = 'testusername'
        m_get_enrollment.return_value = None, None

        params = {
            'course_id': 'course-v1:org+course+run',
            'username': 'testusername',
        }
        response = self.client.get('/api/v1/enrollment/', params)
        self.assertEqual(response.status_code, 200)

        m_get_user.assert_called_once_with(username='testusername')
        m_get_enrollment.assert_called_once_with(
            username='testusername',
            course_id='course-v1:org+course+run',
        )
