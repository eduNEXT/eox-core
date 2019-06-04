#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient


class TestPreEnrollmentsAPI(TestCase):
    """ Tests for the pre-enrollments endpoint """

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """ setup """
        super(TestPreEnrollmentsAPI, self).setUp()
        self.api_user = User('test', 'test@example.com', 'test')
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)

    @patch_permissions
    def test_api_get_input_validation(self, _):
        """ Test the parameter validation of GET method """
        # Test empty request
        response = self.client.get('/api/v1/pre_enrollment/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data.keys())

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.get('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data.values()[0][0])
        self.assertIn('bundle_id', response.data.values()[0][0])

    @patch('eox_core.api.v1.views.get_pre_enrollment')
    @patch_permissions
    def test_api_get(self, _, m_get_pre_enrollment):
        """ Test that the GET method works under normal conditions """
        m_get_pre_enrollment.return_value = None

        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        response = self.client.get('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 200)

        m_get_pre_enrollment.assert_called_once_with(
            email='test@example.com',
            course_id='course-v1:org+course+run',
            auto_enroll=True,
        )

    @patch_permissions
    def test_api_post_input_validation(self, _):
        """ Test the parameter validation of POST method """
        # Test empty request
        response = self.client.post('/api/v1/pre_enrollment/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data.keys())

        # Test request with only email
        params = {
            'email': 'test@example.com',
        }
        response = self.client.post('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data.values()[0][0])
        self.assertIn('bundle_id', response.data.values()[0][0])

        # Test request: email, bundle_id, course_id
        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'bundle_id': 'bund_1245',
        }
        response = self.client.post('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data.values()[0][0])
        self.assertIn('bundle_id', response.data.values()[0][0])

    @patch('eox_core.api.v1.views.pre_enroll_on_program')
    @patch('eox_core.api.v1.views.create_pre_enrollment')
    @patch_permissions
    def test_api_post(self, _, m_create_pre_enrollment, m_pre_enroll_on_program):
        """ Test that the GET method works under normal conditions """
        m_create_pre_enrollment.return_value = None, None
        m_pre_enroll_on_program.return_value = []

        # Test create pre-enrollment to single course
        params = {
            'email': 'test@example.com',
            'course_id': 'course-v1:org+course+run',
            'auto_enroll': True,
        }
        response = self.client.post('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 200)

        m_create_pre_enrollment.assert_called_once_with(
            email='test@example.com',
            course_id='course-v1:org+course+run',
            auto_enroll=True,
        )

        # Test create pre-enrollments for the courses in a program
        params = {
            'email': 'test@example.com',
            'bundle_id': 'bund_1245',
            'auto_enroll': True,
        }
        response = self.client.post('/api/v1/pre_enrollment/', params)
        self.assertEqual(response.status_code, 200)

        m_pre_enroll_on_program.assert_called_once_with(
            email='test@example.com',
            program_uuid='bund_1245',
            auto_enroll=True,
        )