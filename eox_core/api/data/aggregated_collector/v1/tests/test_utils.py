"""
Test suite for Aggregated Data Collector API.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from eox_core.api.data.aggregated_collector.utils import execute_query, fetch_access_token

class UtilsTests(TestCase):
    @patch("eox_core.api.data.aggregated_collector.utils.connection.cursor")
    def test_execute_query_success(self, mock_cursor):
        """
        Test that execute_query returns the expected result when the query executes successfully.
        """
        mock_cursor.return_value.__enter__.return_value.fetchall.return_value = [(1, "test_user")]
        mock_cursor.return_value.__enter__.return_value.description = [("id",), ("username",)]
        
        result = execute_query("SELECT id, username FROM auth_user;")
        expected_result = [{"id": 1, "username": "test_user"}]

        self.assertEqual(result, expected_result)

    @patch("eox_core.api.data.aggregated_collector.utils.connection.cursor")
    def test_execute_query_failure(self, mock_cursor):
        """
        Test that execute_query handles exceptions gracefully.
        """
        mock_cursor.return_value.__enter__.side_effect = Exception("Database error")
        
        result = execute_query("SELECT id, username FROM auth_user;")
        self.assertEqual(result, [])  # Expected to return an empty list on failure

    @patch("eox_core.api.data.aggregated_collector.utils.requests.post")
    def test_fetch_access_token_success(self, mock_post):
        """
        Test that fetch_access_token correctly retrieves an access token.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value = mock_response

        token = fetch_access_token("http://mock-token.com", "client_id", "client_secret")
        self.assertEqual(token, "mock_token")

    @patch("eox_core.api.data.aggregated_collector.utils.requests.post")
    def test_fetch_access_token_failure(self, mock_post):
        """
        Test that fetch_access_token returns None if the request fails.
        """
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_request"}
        mock_post.return_value = mock_response

        token = fetch_access_token("http://mock-token.com", "client_id", "client_secret")
        self.assertIsNone(token)
