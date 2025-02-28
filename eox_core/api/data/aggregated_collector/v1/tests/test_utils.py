"""
Test suite for Aggregated Data Collector API.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from eox_core.api.data.aggregated_collector.utils import execute_query

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
