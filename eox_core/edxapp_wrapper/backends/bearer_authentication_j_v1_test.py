""" Backend test abstraction. """


def get_bearer_authentication():
    """Allow to get the function BearerAuthentication from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py

    Returns:
        BearerAuthentication function.
    """
    try:
        from openedx.core.lib.api.authentication import BearerAuthentication
    except ImportError:
        BearerAuthentication = object
    return BearerAuthentication


def get_bearer_authentication_allow_inactive_user():  # pylint: disable=invalid-name
    """Allow to get the class BearerAuthenticationAllowInactiveUser from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py

    Returns:
        BearerAuthentication function.
    """
    try:
        from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
    except ImportError:
        BearerAuthenticationAllowInactiveUser = object

    return BearerAuthenticationAllowInactiveUser
