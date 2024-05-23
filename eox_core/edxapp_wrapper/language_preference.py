""" Backend abstraction. """
from importlib import import_module

from django.conf import settings


def get_language_preference_middleware(*args, **kwargs):
    """ Get LanguagePreferenceMiddleware. """
    backend_function = settings.EOX_CORE_LANG_PREF_BACKEND
    backend = import_module(backend_function)
    return backend.get_language_preference_middleware(*args, **kwargs)
