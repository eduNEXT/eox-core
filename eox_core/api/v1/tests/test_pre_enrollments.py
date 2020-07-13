#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for PreEnrollments under the open-release/hawthorn.beta1 tag
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import patch
from rest_framework.test import APIClient


class PreEnrollmentsAPITest(TestCase):
    """ Tests for the pre-enrollments endpoint """

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """ setup """
        super(PreEnrollmentsAPITest, self).setUp()
        self.api_user = User('test', 'test@example.com', 'test')
        self.client = APIClient()
        self.url = '/api/v1/pre-enrollment/'
        self.client.force_authenticate(user=self.api_user)

    @patch_permissions
    def test_api_get_input_validation(self, _):
        """ Test the parameter validation of GET method """
        # Test empty request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.views.get_pre_enrollment')
    def test_api_get(self, m_get_pre_enrollment, m_get_valid_course_key, *_):
        """ Test that the GET method works under normal conditions """
        m_get_pre_enrollment.return_value = None

        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        m_get_valid_course_key.return_value = params['course_id']
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)

        m_get_pre_enrollment.assert_called_once_with(**params)

    @patch_permissions
    def test_api_post_input_validation(self, _):
        """ Test the parameter validation of POST method """
        # Test empty request
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.post(self.url, params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.views.create_pre_enrollment')
    def test_api_post(self, m_create_pre_enrollment, m_get_valid_course_key, *_):
        """ Test that the POST method works under normal conditions """
        m_create_pre_enrollment.return_value = None, None

        # Test create pre-enrollment to single course
        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        m_get_valid_course_key.return_value = params['course_id']
        response = self.client.post(self.url, params)
        self.assertEqual(response.status_code, 200)

        m_create_pre_enrollment.assert_called_once_with(**params)

    @patch_permissions
    def test_api_put_input_validation(self, _):
        """ Test the parameter validation of PUT method """
        # Test empty request
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.put(self.url, params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.views.get_pre_enrollment')
    @patch('eox_core.api.v1.views.update_pre_enrollment')
    def test_api_put(self, m_update_pre_enrollment, m_get_pre_enrollment, m_get_valid_course_key, *_):
        """ Test that the PUT method works under normal conditions """
        m_update_pre_enrollment.return_value = None
        m_pre_enrollment = {
            "warning": "",
            "course_id": "course-v1:org+course+run",
            "auto_enroll": True,
            "email": "test@example.com"
        }
        m_get_pre_enrollment.return_value = m_pre_enrollment
        m_get_valid_course_key.return_value = m_pre_enrollment['course_id']

        # Test update pre-enrollment
        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        response = self.client.put(self.url, params)
        self.assertEqual(response.status_code, 200)

        m_update_pre_enrollment.assert_called_once_with(
            auto_enroll=True,
            pre_enrollment=m_pre_enrollment,
        )

        m_get_pre_enrollment.assert_called_once_with(
            email='test@example.com',
            course_id='course-v1:org+course+run'
        )

    @patch_permissions
    def test_api_delete_validation(self, _):
        """ Test the parameter validation of DELETE method """
        # Test empty request
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.delete(self.url, params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.views.get_pre_enrollment')
    @patch('eox_core.api.v1.views.delete_pre_enrollment')
    def test_api_delete(self, m_delete_pre_enrollment, m_get_pre_enrollment, m_get_valid_course_key, *_):
        """ Test that the DELETE method works under normal conditions """
        m_delete_pre_enrollment.return_value = None
        m_pre_enrollment = {
            "warning": "",
            "course_id": "course-v1:org+course+run",
            "auto_enroll": True,
            "email": "test@example.com"
        }
        m_get_pre_enrollment.return_value = m_pre_enrollment
        m_get_valid_course_key.return_value = m_pre_enrollment['course_id']
        # Test delete pre-enrollment
        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        response = self.client.delete(self.url, params)
        self.assertEqual(response.status_code, 204)

        m_delete_pre_enrollment.assert_called_once_with(
            pre_enrollment=m_pre_enrollment,
        )

        m_get_pre_enrollment.assert_called_once_with(
            email='test@example.com',
            course_id='course-v1:org+course+run'
        )
