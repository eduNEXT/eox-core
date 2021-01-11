""" Backend test abstraction. """


def get_bearer_authentication():
    """Allow to get the function BearerAuthentication from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/lib/api/authentication.py

    Returns:
        BearerAuthentication function.
    """
    try:
        from openedx.core.lib.api.authentication import BearerAuthentication  # pylint: disable=import-outside-toplevel
    except ImportError:
        BearerAuthentication = object
    return BearerAuthentication
