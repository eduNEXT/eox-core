"""Backend for authentication.

This file contains all the necessary authentication dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py
"""
from openedx.core.lib.api.authentication import BearerAuthentication  # pylint: disable=import-error


def get_bearer_authentication():
    """Allow to get the function BearerAuthentication from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py

    Returns:
        BearerAuthentication function.
    """
    return BearerAuthentication
