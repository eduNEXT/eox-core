#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test module for Users API.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from mock import Mock, patch
from rest_framework.exceptions import NotFound
from rest_framework.test import APIClient


class UserAPITest(TestCase):
    """ Tests for the User API. """

    patch_permissions = patch('eox_core.api.v1.permissions.EoxCoreAPIPermission.has_permission', return_value=True)

    def setUp(self):
        """ Setup. """
        super(UserAPITest, self).setUp()
        self.api_user = User(1, 'api_client@example.com', 'client')
        self.client = APIClient()
        self.url = '/api/v1/user/'
        self.client.force_authenticate(user=self.api_user)
        self.data = {
            "username": "test",
            "bio": "...",
            "name": "Test t",
            "country": "TestLand",
            "year_of_birth": 1880,
        }

    @patch_permissions
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_get_validation(self, m_get_edxapp_user, *_):
        """ Test the paremeter validation of the GET method. """
        m_get_edxapp_user.return_value = None

        # Test empty request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Email', response.data[0])
        self.assertIn('username', response.data[0])

    @patch_permissions
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_get_invalid_user(self, m_get_edxapp_user, *_):
        """ Test the GET method fails for an invalid user. """
        params = {
            'email': 'test@test.com',
        }

        m_get_edxapp_user.side_effect = NotFound('No user found by {query} on site example.com.'.format(query=str(params)))

        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 404)

    @patch_permissions
    @patch('eox_core.api.v1.views.EdxappUserReadOnlySerializer')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_get(self, m_get_edxapp_user, m_EdxappUserReadOnlySerializer, *_):  # pylint: disable=invalid-name
        """ Test that the GET method works under normal conditions. """
        m_get_edxapp_user.return_value = Mock()
        m_EdxappUserReadOnlySerializer.return_value = self

        params = {
            'username': 'test',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(self.data, response.data)
        m_get_edxapp_user.assert_called_once_with(**params)

    @patch_permissions
    @patch('eox_core.api.v1.views.delete_edxapp_user')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_delete_invalid_user(self, m_get_edxapp_user, m_delete_edxapp_user, *_):
        """ Test the DELETE method fails for an invalid user. """
        params = {
            'email': 'test@test.com',
        }

        m_get_edxapp_user.side_effect = NotFound('No user found by {query} on site example.com.'.format(query=str(params)))

        response = self.client.delete(self.url, params)
        self.assertEqual(response.status_code, 404)
        m_delete_edxapp_user.assert_not_called()

    @patch_permissions
    @patch('eox_core.api.v1.views.delete_edxapp_user')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_delete(self, m_get_edxapp_user, m_delete_edxapp_user, *_):
        """ Test that the DELETE method works under normal conditions. """
        m_user = User(2, 'test@example.com', 'test')
        m_get_edxapp_user.return_value = m_user
        m_delete_edxapp_user.return_value = None

        params = {
            'username': 'test',
        }
        response = self.client.delete(self.url, params)
        self.assertEqual(response.status_code, 204)
        m_get_edxapp_user.assert_called_once_with(**params)
        m_delete_edxapp_user.assert_called_once_with(m_user)

    @patch_permissions
    @patch('eox_core.api.v1.views.EdxappUserReadOnlySerializer')
    @patch('eox_core.api.v1.views.update_edxapp_user')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_put(self, m_get_edxapp_user, m_update_edxapp_user, m_EdxappUserReadOnlySerializer, *_):  # pylint: disable=invalid-name
        """ Test that the PUT method works under normal conditions. """
        m_user = User(2, 'test@example.com', 'test')
        self.data['name'] = 'Updated name'
        m_EdxappUserReadOnlySerializer.return_value = self
        m_get_edxapp_user.return_value = m_user
        m_update_edxapp_user.return_value = None

        params = {
            'username': 'test',
            'name': 'Updated name',
        }

        response = self.client.put(self.url, data=params, format='json')
        self.assertEqual(response.status_code, 200)
        m_get_edxapp_user.assert_called_once()
        self.assertDictContainsSubset(self.data, response.data)
        m_update_edxapp_user.assert_called_once_with(m_user, name='Updated name')

    @patch_permissions
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_put_force_validation(self, m_get_edxapp_user, *_):
        """
        Test that the PUT method validates a reason is given when setting
        the force param to change email or password.
        """
        m_user = User(2, 'test@example.com', 'test')
        m_get_edxapp_user.return_value = m_user

        params = {
            'username': 'test',
            'email': 'updated_test@example.com',
            'force': True,
        }

        response = self.client.put(self.url, data=params, format='json')
        self.assertEqual(response.status_code, 404)
        m_get_edxapp_user.assert_called_once()
        self.assertIn('reason', response.data['detail'])

    @patch_permissions
    @patch('eox_core.api.v1.views.EdxappUserReadOnlySerializer')
    @patch('eox_core.api.v1.views.update_edxapp_user')
    @patch('eox_core.api.v1.views.get_edxapp_user')
    def test_api_put_force(self, m_get_edxapp_user, m_update_edxapp_user, m_EdxappUserReadOnlySerializer, *_):  # pylint: disable=invalid-name
        """ Test that the PUT method with force works under normal conditions. """
        m_user = User(2, 'test@example.com', 'test')
        self.data['email'] = 'updated_test@example.com'
        m_EdxappUserReadOnlySerializer.return_value = self
        m_get_edxapp_user.return_value = m_user
        m_update_edxapp_user.return_value = None

        params = {
            'username': 'test',
            'email': 'updated_test@example.com',
            'force': True,
            'reason': '...',
        }

        response = self.client.put(self.url, data=params, format='json')
        self.assertEqual(response.status_code, 200)
        m_get_edxapp_user.assert_called_once()
        self.assertDictContainsSubset(self.data, response.data)
        params.pop('username')
        m_update_edxapp_user.assert_called_once_with(m_user, **params)
