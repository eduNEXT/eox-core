""" Backend abstraction. """
from importlib import import_module

from django.conf import settings


def get_configuration_helper(*args, **kwargs):
    """ Get configuration helper module """
    backend_function = settings.EOX_CORE_CONFIGURATION_HELPER_BACKEND
    backend = import_module(backend_function)
    return backend.get_configuration_helper(*args, **kwargs)
