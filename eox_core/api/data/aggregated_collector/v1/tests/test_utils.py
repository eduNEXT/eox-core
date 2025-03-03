"""
Test suite for Aggregated Data Collector API.
"""
from unittest.mock import patch

from django.test import TestCase

from eox_core.api.data.aggregated_collector.utils import execute_query


class UtilsTests(TestCase):
    """
    Test suite for utility functions used in the Aggregated Data Collector API.
    """
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
    def test_execute_query_empty_result(self, mock_cursor):
        """
        Test that execute_query returns an empty list when there are no results.
        """
        mock_cursor.return_value.__enter__.return_value.fetchall.return_value = []
        mock_cursor.return_value.__enter__.return_value.description = [("id",), ("username",)]

        result = execute_query("SELECT id, username FROM auth_user;")

        self.assertEqual(result, [])

    @patch("eox_core.api.data.aggregated_collector.utils.connection.cursor")
    def test_execute_query_multiple_rows(self, mock_cursor):
        """
        Test that execute_query correctly handles multiple rows in the result.
        """
        mock_cursor.return_value.__enter__.return_value.fetchall.return_value = [
            (1, "test_user1"),
            (2, "test_user2"),
        ]
        mock_cursor.return_value.__enter__.return_value.description = [("id",), ("username",)]

        result = execute_query("SELECT id, username FROM auth_user;")
        expected_result = [
            {"id": 1, "username": "test_user1"},
            {"id": 2, "username": "test_user2"},
        ]

        self.assertEqual(result, expected_result)
