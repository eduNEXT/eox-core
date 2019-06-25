""" Backend abstraction. """
from importlib import import_module
from django.conf import settings


def get_microsite(*args, **kwargs):
    """ Get microsite module """
    backend_function = settings.EOX_CORE_MICROSITES_BACKEND
    backend = import_module(backend_function)
    return backend.get_microsite(*args, **kwargs)
