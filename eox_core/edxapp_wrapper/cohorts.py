"""
Users public function definitions
"""
from importlib import import_module

from django.conf import settings


def get_user_cohort(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_USER_COHORT_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_cohort(*args, **kwargs)
