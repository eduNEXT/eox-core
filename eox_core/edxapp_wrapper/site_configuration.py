"""
Site configuration definitions.
"""

from importlib import import_module
from django.conf import settings


def get_all_orgs_helper():
    """ Gets the get_all_orgs_helper function. """

    backend_function = settings.EOX_CORE_SITE_CONFIGURATION
    backend = import_module(backend_function)

    return backend.get_all_orgs_helper()
