"""
Authentication definitions.
"""
from importlib import import_module

from django.conf import settings


def get_bearer_authentication():
    """ Gets BearerAuthentication class. """
    backend_function = settings.EOX_CORE_BEARER_AUTHENTICATION
    backend = import_module(backend_function)

    return backend.get_bearer_authentication()


BearerAuthentication = get_bearer_authentication()  # pylint: disable=invalid-name
