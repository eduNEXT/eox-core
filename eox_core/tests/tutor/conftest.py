"""
The conftest module sets up the database connection for pytest-django.

The integration tests will reuse the database from tutor local so a noop
django_db_setup is required.
See: https://pytest-django.readthedocs.io/en/latest/database.html
"""

import pytest  # pylint: disable=import-error


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Makes the tests reuse the existing database
    """
