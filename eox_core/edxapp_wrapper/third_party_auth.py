"""
Third Party Auth Exception Middleware definitions.
"""

from importlib import import_module

from django.conf import settings


def get_tpa_exception_middleware():
    """Get the ExceptionMiddleware class."""
    backend_function = settings.EOX_CORE_THIRD_PARTY_AUTH_BACKEND
    backend = import_module(backend_function)
    return backend.get_tpa_exception_middleware()
