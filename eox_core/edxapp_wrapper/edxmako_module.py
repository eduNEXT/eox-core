""" Edxmako backend abstraction. """
from importlib import import_module

from django.conf import settings


def render_to_response(*args, **kwargs):
    """ Return render to response. """

    backend_function = settings.EDXMAKO_MODULE
    backend = import_module(backend_function)

    return backend.render_to_response(*args, **kwargs)
