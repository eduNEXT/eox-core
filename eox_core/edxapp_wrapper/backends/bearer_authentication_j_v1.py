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


def get_bearer_authentication_allow_inactive_user():  # pylint: disable=invalid-name
    """Allow to get the class BearerAuthenticationAllowInactiveUser from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py

    Returns:
        BearerAuthenticationAllowInactiveUser class.
    """
    try:
        from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
    except ImportError:
        # This import is just for backwards compatibility in ironwood versions.
        from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser

        return OAuth2AuthenticationAllowInactiveUser

    return BearerAuthenticationAllowInactiveUser
