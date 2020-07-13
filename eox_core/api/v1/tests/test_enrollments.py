# -*- coding: utf-8 -*-
""" . """
from django.contrib.auth.models import User
from django.test import TestCase
from mock import patch
from rest_framework.test import APIClient


class TestEnrollmentsAPI(TestCase):
    """ Tests for the enrollments endpoints """

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """ setup """
        super(TestEnrollmentsAPI, self).setUp()
        self.api_user = User(1, 'test@example.com', 'test')
        self.client = APIClient()
        self.client.force_authenticate(user=self.api_user)

    @patch_permissions
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_get_validation(self, m_get_user, *_):
        """ Test that the GET method requires some parameters """
        response = self.client.get('/api/v1/enrollment/')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data[0])

        params = {
            'username': 'test',
        }
        response = self.client.get('/api/v1/enrollment/', params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('course_id', response.data[0])

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

    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', )
    @patch_permissions
    def test_api_post_validation(self, _, m_check_enrollment):
        """ Test that the POST method validates inputs """
        response = self.client.post('/api/v1/enrollment/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('mode', response.data)

        m_check_enrollment.return_value = ['Email or username needed']
        params = {
            'mode': 'audit',
        }
        response = self.client.post('/api/v1/enrollment/', data=params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)

        m_check_enrollment.return_value = ['You have to provide a course_id or bundle_id']
        params = {
            'mode': 'audit',
            'username': 'test',
        }
        response = self.client.post('/api/v1/enrollment/', data=params)
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', return_value=[])
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch('eox_core.api.v1.views.create_enrollment')
    def test_api_post_works(self, m_create_enrollment, *_):
        """ Test that the POST method works in normal conditions """

        m_enrollment = {
            'mode': 'audit',
            'user': 'test',  # this is the source value for the username field in the serializer
            'course_id': 'course-v1:org+course+run',
            'is_active': True,
        }
        m_create_enrollment.return_value = m_enrollment, None
        params = {
            'mode': 'audit',
            'username': 'test',
            'course_id': 'course-v1:org+course+run',
        }
        response = self.client.post('/api/v1/enrollment/', data=params)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(params, response.data)

    @patch_permissions
    @patch('eox_core.api.v1.serializers.validate_org')
    @patch('eox_core.api.v1.serializers.get_valid_course_key')
    @patch('eox_core.api.v1.serializers.check_edxapp_enrollment_is_valid', return_value=[])
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch('eox_core.api.v1.views.update_enrollment')
    def test_api_put_works(self, m_update_enrollment, m_get_user, *_):
        """ Test that the PUT method works in normal conditions with a list of enrollments """

        enrollments_response = {
            'mode': 'audit',
            'user': 'test',  # this is the source value for the username field in the serializer
            'course_id': 'course-v1:org+course+run',
            'is_active': True,
        }

        m_update_enrollment.return_value = enrollments_response
        params = [{
            'mode': 'audit',
            'username': 'test',
            'course_id': 'course-v1:org+course+run',
        }, {
            'mode': 'audit',
            'username': 'test',
            'course_id': 'course-v1:org+course_2+run',
        }]

        response = self.client.put('/api/v1/enrollment/', data=params, format='json')
        m_get_user.assert_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('course_id', response.data[0])
        self.assertIn('is_active', response.data[0])
        self.assertEqual(2, len(response.data))

    @patch_permissions
    @patch('eox_core.api.v1.views.get_edxapp_user')
    @patch('eox_core.api.v1.views.delete_enrollment')
    def test_api_delete_works(self, m_delete_enrollment, m_get_user, *_):
        """ Test that the DELETE method works in normal conditions with a bundle """

        params = {
            'username': 'test',
            'course_id': 'course-v1:org+course+run',
        }
        response = self.client.delete('/api/v1/enrollment/', params)
        m_get_user.assert_called_once_with(username='test')
        m_delete_enrollment.assert_called_once_with(course_id='course-v1:org+course+run', user=m_get_user.return_value)
        self.assertEqual(response.status_code, 204)
